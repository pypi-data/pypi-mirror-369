from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set
from uuid import uuid4

from jsonschema import validate as jsonschema_validate, ValidationError

from natbus.client import NatsBus
from natbus.message import BusMessage, ReceivedMessage

from .config import LlmAgentConfig
from .registry import CommandRegistry, CommandMapping
from .schemas import LlmPlan, FinalReply
from .abilities import AbilityCatalog
from .canonicalizer import LlmCanonicalizer  # intent canonicalizer


class _NoopLogger:
    def debug(self, *a, **kw): pass
    def info(self, *a, **kw): pass
    def warning(self, *a, **kw): pass
    def error(self, *a, **kw): pass
    def exception(self, *a, **kw): pass


class CanonicalizationError(Exception):
    pass


@dataclass
class PendingRequest:
    reply_subject: str
    original_command: str
    mapping: CommandMapping
    iterative: bool  # re-plan after observations when True


class LlmNatbusAgent:
    """
    NatBus ↔ LLM planner/actor.

    • Accepts human commands on cfg.human_command_subject
    • Calls injected llm_call(prompt, system) to obtain a plan (JSON)
    • Publishes service requests per plan; tracks correlation for responses
    • Iterative mode: after each observation, calls LLM again to decide next step or finalize
    • Validates plan payloads against mapping/ability JSON Schemas when provided
    • Canonicalization: free text → known command; schema-guided arg completion before planning
    """

    def __init__(
        self,
        bus: NatsBus,
        llm_call,
        registry: CommandRegistry,
        cfg: Optional[LlmAgentConfig] = None,
        abilities: Optional[AbilityCatalog] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.bus = bus
        self.llm_call = llm_call  # async: (prompt: str, system: Optional[str]) -> str
        self.registry = registry
        self.cfg = cfg or LlmAgentConfig()
        self.abilities = abilities or AbilityCatalog()

        self._pending: Dict[str, PendingRequest] = {}
        self._pending_ts: Dict[str, float] = {}
        self._started = False
        self._gc_task: Optional[asyncio.Task] = None

        self._resp_subscribed: Set[str] = set()
        self.log = logger or _NoopLogger()

        # Intent canonicalizer (command mapping)
        self._canonicalizer: Optional[LlmCanonicalizer] = None
        if self.cfg.enable_canonicalization:
            self._canonicalizer = LlmCanonicalizer(
                llm_call=self.llm_call,
                min_confidence=self.cfg.canonicalization_min_confidence,
                max_attempts=getattr(self.cfg, "canon_max_attempts", 1),
            )

    # -------------------------------------------------------------------------
    async def start(self) -> None:
        if self._started:
            return
        self._started = True

        self.log.debug("agent_start_subscribe_human", extra={
            "subject": self.cfg.human_command_subject
        })
        await self.bus.push_subscribe(
            self.cfg.human_command_subject,
            handler=self._on_human_command,
            durable="ai-gateway-human",
            queue="ai-gateway",
        )

        subjects = set(self.registry.all_response_subjects())
        subjects.update(getattr(self.cfg, "extra_response_subjects", ()) or ())
        for ability in self.abilities.as_contract().values():
            resp = ability.get("response_subject")
            if resp:
                subjects.add(resp)

        self.log.debug("agent_start_resp_subjects", extra={"subjects": sorted(subjects)})
        for subj in subjects:
            await self._ensure_response_subscribed(subj)

        self._gc_task = asyncio.create_task(self._gc_pending_loop())
        self.log.debug("agent_started_ok")

    async def close(self) -> None:
        self.log.debug("agent_close_begin", extra={"pending": len(self._pending)})
        if self._gc_task:
            self._gc_task.cancel()
            try:
                await self._gc_task
            except asyncio.CancelledError:
                pass
        self._started = False
        self.log.debug("agent_close_done")

    async def _gc_pending_loop(self) -> None:
        try:
            while True:
                await asyncio.sleep(5)
                self._expire_pending()
        except asyncio.CancelledError:
            return

    def _expire_pending(self) -> None:
        if not self._pending:
            return
        now = asyncio.get_event_loop().time()
        ttl = getattr(self.cfg, "pending_timeout_seconds", 60.0)
        expired = [cid for cid, ts in self._pending_ts.items() if now - ts > ttl]
        for cid in expired:
            ctx = self._pending.pop(cid, None)
            self._pending_ts.pop(cid, None)
            if ctx:
                self.log.warning("pending_expired", extra={
                    "corr": cid, "cmd": ctx.original_command, "ttl": ttl
                })
        if expired:
            self.log.debug("pending_gc_summary", extra={"removed": len(expired), "remaining": len(self._pending)})

    @staticmethod
    def _sanitize(s: str) -> str:
        return s.replace(".", "-").replace("*", "star").replace(">", "gt")

    async def _ensure_response_subscribed(self, subject: Optional[str]) -> None:
        if not subject or subject in self._resp_subscribed:
            return
        self.log.debug("subscribe_response_subject", extra={"subject": subject})
        await self.bus.push_subscribe(
            subject,
            handler=self._on_service_response,
            durable=f"ai-gateway-resp-{self._sanitize(subject)}",
            queue="ai-gateway",
        )
        self._resp_subscribed.add(subject)

    # -------------------------------------------------------------------------
    async def _on_human_command(self, rm: ReceivedMessage) -> None:
        try:
            payload = rm.as_json()
        except Exception as e:
            self.log.error("human_cmd_bad_json", extra={"error": str(e)})
            await rm.ack()
            return

        raw_cmd_text = str(payload.get("cmd", "")).strip()
        cmd_lc = raw_cmd_text.lower()
        args = payload.get("args", {}) or {}
        reply_subject = str(payload.get("reply_subject") or self.cfg.default_reply_subject)
        correlation_id = rm.correlation_id or rm.trace_id or str(uuid4())

        self.log.debug("human_cmd_received", extra={
            "corr": correlation_id,
            "cmd": raw_cmd_text,
            "args_keys": sorted(list(args.keys())),
            "reply_subject": reply_subject
        })

        def _prefix_match(cmd_text: str) -> Optional[str]:
            best = None
            for key in self.registry.list_commands():
                if cmd_text.startswith(key):
                    if len(cmd_text) == len(key) or cmd_text[len(key)] in " \t\r\n?.!,;:/-":
                        if best is None or len(key) > len(best):
                            best = key
            return best

        mapping = self.registry.get(cmd_lc)
        effective_cmd = cmd_lc
        effective_args = dict(args)

        if not mapping:
            pref = _prefix_match(cmd_lc)
            if pref:
                self.log.debug("human_cmd_prefix_match", extra={"corr": correlation_id, "matched": pref})
                mapping = self.registry.get(pref)
                effective_cmd = pref

        # ------------- Canonicalization (intent) -------------
        if not mapping and self._canonicalizer is not None:
            self.log.debug("canon_try", extra={"corr": correlation_id, "text": cmd_lc})
            try:
                canon = await self._canonicalizer.canonicalize(cmd_lc, self.abilities, self.registry)
            except Exception as e:
                self.log.warning("canon_error", extra={"corr": correlation_id, "error": str(e)})
                canon = None

            conf = float(getattr(canon, "confidence", 0.0) or 0.0) if canon else 0.0
            self.log.debug("canon_result", extra={
                "corr": correlation_id,
                "found": bool(canon),
                "command": getattr(canon, "command", None),
                "confidence": conf
            })
            if canon is not None and conf >= float(getattr(self.cfg, "canonicalization_min_confidence", 0.6)):
                m2 = self.registry.get(canon.command)
                if m2 is None:
                    await self._reply_json(
                        reply_subject, {"error": "unknown_command", "cmd": raw_cmd_text}, rm, corr_id=correlation_id
                    )
                    await rm.ack()
                    return
                mapping = m2
                effective_cmd = canon.command.strip().lower()
                for k, v in (getattr(canon, "args", {}) or {}).items():
                    if v is not None:
                        effective_args.setdefault(k, v)
                self.log.debug("canon_applied", extra={
                    "corr": correlation_id,
                    "effective_cmd": effective_cmd,
                    "args_keys": sorted(list(effective_args.keys()))
                })
            else:
                await self._reply_json(
                    reply_subject, {"error": "unknown_command", "cmd": raw_cmd_text}, rm, corr_id=correlation_id
                )
                await rm.ack()
                return

        if not mapping:
            await self._reply_json(
                reply_subject, {"error": "unknown_command", "cmd": raw_cmd_text}, rm, corr_id=correlation_id
            )
            await rm.ack()
            return

        # ------------- Schema-guided completion BEFORE planning -------------
        schema = mapping.request_schema or {}
        required = list(schema.get("required", []) or [])

        def _missing(req_keys: list[str], current: dict) -> list[str]:
            miss = []
            for k in req_keys:
                if k not in current or current[k] in (None, "", [], {}):
                    miss.append(k)
            return miss

        pre_missing = _missing(required, effective_args)
        self.log.debug("args_pre_fill", extra={
            "corr": correlation_id,
            "required": required,
            "missing": pre_missing,
            "have_keys": sorted(list(effective_args.keys()))
        })
        if pre_missing and self._canonicalizer is not None:
            try:
                fills = await self._canonicalizer.fill_required_args(
                    command_text=raw_cmd_text,
                    mapping=mapping,
                    current_args=dict(effective_args),
                    max_attempts=getattr(self.cfg, "canonicalization_max_attempts", 1),
                )
                self.log.debug("args_fill_result", extra={
                    "corr": correlation_id,
                    "filled_keys": sorted(list((fills or {}).keys()))
                })
            except Exception as e:
                self.log.warning("args_fill_error", extra={"corr": correlation_id, "error": str(e)})
                await self._reply_json(
                    reply_subject, {"error": "canonicalization_failed", "detail": str(e)}, rm, corr_id=correlation_id
                )
                if not getattr(self.cfg, "ack_on_canon_failure", True):
                    self.log.debug("ack_on_canon_failure_false_ack_anyway", extra={"corr": correlation_id})
                await rm.ack()
                return
            if isinstance(fills, dict):
                for k, v in fills.items():
                    if v is not None and (not required or k in required):
                        effective_args.setdefault(k, v)

        post_missing = _missing(required, effective_args)
        self.log.debug("args_post_fill", extra={
            "corr": correlation_id,
            "missing": post_missing,
            "final_keys": sorted(list(effective_args.keys()))
        })
        if post_missing:
            await self._reply_json(
                reply_subject,
                {"error": "missing_required_args",
                 "detail": {"missing": post_missing, "example": mapping.example_payload or {}}},
                rm,
                corr_id=correlation_id,
            )
            await rm.ack()
            return

        # ------------- Plan -------------
        self.log.debug("plan_begin", extra={
            "corr": correlation_id,
            "cmd": effective_cmd,
            "subject_default": mapping.request_subject
        })
        try:
            plan = await self._llm_plan(effective_cmd, effective_args, mapping)
        except Exception as e:
            self.log.debug("plan_error", extra={"corr": correlation_id, "error": str(e)})
            await self._reply_json(
                reply_subject, {"error": "invalid_llm_output", "detail": str(e)}, rm, corr_id=correlation_id
            )
            await rm.ack()
            return

        self.log.debug("plan_ok", extra={
            "corr": correlation_id,
            "action": plan.action,
            "subject": plan.subject,
            "await_response": plan.await_response
        })

        if plan.action != "send_request":
            await self._reply_json(
                reply_subject, {"error": "unsupported_action", "action": plan.action}, rm, corr_id=correlation_id
            )
            await rm.ack()
            return

        await self._publish_service_request(plan, correlation_id, effective_cmd)

        if plan.await_response:
            resp_subject = plan.response_subject or mapping.response_subject
            if not resp_subject:
                self.log.debug("plan_no_resp_subject", extra={"corr": correlation_id})
                await self._reply_json(
                    reply_subject, {"error": "no_response_subject_configured"}, rm, corr_id=correlation_id
                )
            else:
                await self._ensure_response_subscribed(resp_subject)
                iterative = mapping.llm_iterative if mapping.llm_iterative is not None else getattr(
                    self.cfg, "llm_iterative_default", True
                )
                self._pending[correlation_id] = PendingRequest(
                    reply_subject=reply_subject,
                    original_command=effective_cmd,
                    mapping=mapping,
                    iterative=iterative,
                )
                self._pending_ts[correlation_id] = asyncio.get_event_loop().time()
                self.log.debug("pending_add", extra={
                    "corr": correlation_id, "resp_subject": resp_subject, "iterative": iterative
                })
        else:
            await self._reply_json(
                reply_subject,
                {"status": "sent", "subject": plan.subject, "correlation_id": correlation_id},
                rm,
                corr_id=correlation_id,
            )
            self.log.debug("sent_no_await", extra={"corr": correlation_id, "subject": plan.subject})

        await rm.ack()
        self.log.debug("human_cmd_ack", extra={"corr": correlation_id})

    async def _on_service_response(self, rm: ReceivedMessage) -> None:
        correlation_id = rm.correlation_id or ""
        self.log.debug("service_resp_rx", extra={"corr": correlation_id, "subject": rm.subject})
        ctx = self._pending.get(correlation_id)
        if not ctx:
            self.log.debug("service_resp_no_ctx", extra={"corr": correlation_id})
            await rm.ack()
            return

        try:
            observation = rm.as_json()
            obs_type = "json"
        except Exception:
            observation = {"raw": rm.as_text()}
            obs_type = "text"

        self.log.debug("service_resp_observation", extra={
            "corr": correlation_id,
            "type": obs_type,
            "keys": list(observation.keys())[:8]
        })

        if ctx.iterative:
            try:
                decision = await self._llm_iterate(ctx.original_command, observation)
            except Exception as e:
                self.log.debug("iterate_error", extra={"corr": correlation_id, "error": str(e)})
                await self._reply_json(
                    ctx.reply_subject,
                    {
                        "correlation_id": correlation_id,
                        "command": ctx.original_command,
                        "data": observation,
                        "note": f"iteration_error: {e}",
                    },
                    rm,
                    corr_id=correlation_id,
                )
                self._pending.pop(correlation_id, None)
                self._pending_ts.pop(correlation_id, None)
                await rm.ack()
                return

            if isinstance(decision, LlmPlan) and decision.action == "send_request":
                self.log.debug("iterate_plan", extra={
                    "corr": correlation_id, "subject": decision.subject, "await_response": decision.await_response
                })
                await self._publish_service_request(decision, correlation_id, ctx.original_command)
                if decision.await_response:
                    next_resp = decision.response_subject or ctx.mapping.response_subject
                    await self._ensure_response_subscribed(next_resp)
                    self._pending_ts[correlation_id] = asyncio.get_event_loop().time()
                    await rm.ack()
                    self.log.debug("iterate_wait_next", extra={"corr": correlation_id, "next_resp": next_resp})
                    return
                await self._reply_json(
                    ctx.reply_subject,
                    {"status": "sent", "subject": decision.subject, "correlation_id": correlation_id},
                    rm,
                    corr_id=correlation_id,
                )
                self._pending.pop(correlation_id, None)
                self._pending_ts.pop(correlation_id, None)
                await rm.ack()
                self.log.debug("iterate_done_no_await", extra={"corr": correlation_id})
                return

            if isinstance(decision, FinalReply):
                self.log.debug("iterate_final_reply", extra={"corr": correlation_id})
                await self._reply_json(
                    ctx.reply_subject,
                    {"correlation_id": correlation_id, "command": ctx.original_command, "data": decision.result},
                    rm,
                    corr_id=correlation_id,
                )
                self._pending.pop(correlation_id, None)
                self._pending_ts.pop(correlation_id, None)
                await rm.ack()
                return

            self.log.debug("iterate_unknown_decision", extra={"corr": correlation_id, "type": type(decision).__name__})
            await self._reply_json(
                ctx.reply_subject,
                {"correlation_id": correlation_id, "command": ctx.original_command, "data": observation},
                rm,
                corr_id=correlation_id,
            )
            self._pending.pop(correlation_id, None)
            self._pending_ts.pop(correlation_id, None)
            await rm.ack()
            return

        # Non-iterative path
        self.log.debug("service_resp_non_iterative", extra={"corr": correlation_id})
        await self._reply_json(
            ctx.reply_subject,
            {"correlation_id": correlation_id, "command": ctx.original_command, "data": observation},
            rm,
            corr_id=correlation_id,
        )
        self._pending.pop(correlation_id, None)
        self._pending_ts.pop(correlation_id, None)
        await rm.ack()

    # -------------------------------------------------------------------------
    # Schema-guided argument canonicalization (fills required fields before planning)
    # -------------------------------------------------------------------------
    async def _canonicalize_args(self, cmd_text: str, raw_args: Dict[str, Any], mapping: CommandMapping) -> Dict[str, Any]:
        schema = mapping.request_schema
        if not getattr(self.cfg, "enable_canonicalization", True) or not schema:
            args = dict(raw_args or {})
            self._normalize_fx_fields(cmd_text, args)
            return args

        args = dict(raw_args or {})
        self._normalize_fx_fields(cmd_text, args)

        if self._satisfies_schema(args, schema):
            return args

        attempts = max(1, int(getattr(self.cfg, "canon_max_attempts", 1)))
        for i in range(attempts):
            self.log.debug("schema_extract_attempt", extra={"attempt": i + 1})
            extracted = await self._schema_guided_extract(cmd_text, args, schema)
            if isinstance(extracted, dict):
                args.update(extracted)
                self._normalize_fx_fields(cmd_text, args)
                self.log.debug("schema_extract_keys", extra={"keys": sorted(list(extracted.keys()))})
            if self._satisfies_schema(args, schema):
                return args

        required = list(schema.get("required") or [])
        missing = [k for k in required if k not in args or args[k] in (None, "", [])]
        raise CanonicalizationError(f"missing required fields: {missing} for command '{mapping.command}'")

    def _normalize_fx_fields(self, cmd_text: Optional[str], args: Dict[str, Any]) -> None:
        before = dict(args)
        sym = str(args.get("symbol") or "").upper().replace("/", "").strip()
        if len(sym) == 6 and sym.isalpha():
            args["symbol"] = sym
        else:
            pair = str(args.get("pair") or "").upper().replace("/", "").strip()
            if len(pair) == 6 and pair.isalpha():
                args["symbol"] = pair
            else:
                t = (cmd_text or "").upper()
                m = re.search(r'\b([A-Z]{3})[\/\s]?([A-Z]{3})\b', t)
                if m:
                    args["symbol"] = m.group(1) + m.group(2)
        if before != args:
            self.log.debug("fx_normalized_args", extra={"before": before, "after": args})

    async def _schema_guided_extract(self, cmd_text: str, known_args: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        system = "Extract and complete required arguments for a trading command. Output strictly valid JSON only."
        prompt = (
            "User text:\n"
            f"{cmd_text}\n\n"
            "Known arguments (may be incomplete):\n"
            f"{json.dumps(known_args)}\n\n"
            "Produce a JSON object that satisfies this JSON Schema. "
            "Only include keys defined by the schema. Do not include explanations.\n"
            f"Schema:\n{json.dumps(schema)}"
        )
        self.log.debug("schema_extract_llm_call", extra={
            "prompt_chars": len(prompt)
        })
        obj = await self._llm_json(system=system, prompt=prompt, required_keys=None, max_retries=1)
        self.log.debug("schema_extract_llm_ok", extra={"keys": sorted(list(obj.keys())) if isinstance(obj, dict) else []})
        return obj if isinstance(obj, dict) else {}

    def _satisfies_schema(self, args: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        req = schema.get("required") or []
        for k in req:
            if k not in args or args[k] in (None, "", []):
                return False
        props = schema.get("properties") or {}
        for k, spec in props.items():
            if k in args and isinstance(spec, dict):
                pat = spec.get("pattern")
                if pat and isinstance(args[k], str):
                    if re.fullmatch(pat, args[k]) is None:
                        return False
        return True

    # -------------------------------------------------------------------------
    async def _publish_service_request(self, plan: LlmPlan, correlation_id: str, origin_cmd: str) -> None:
        ability = self.abilities.get_by_subject(plan.subject)
        if ability and ability.payload_schema:
            self._validate_payload(plan.payload, ability.payload_schema)

        self.log.debug("publish_request", extra={
            "corr": correlation_id,
            "subject": plan.subject,
            "payload_keys": sorted(list((plan.payload or {}).keys()))
        })

        msg = BusMessage.from_json(
            plan.subject,
            plan.payload,
            sender="ai-gateway",
            correlation_id=correlation_id,
            headers={"x-origin-cmd": origin_cmd},
            ensure_trace=True,
            compress=getattr(self.cfg, "compress_outbound", False),
        )
        await self.bus.publish(msg)

    def _validate_payload(self, payload: dict, schema: dict) -> None:
        try:
            jsonschema_validate(payload, schema)
        except ValidationError as e:
            path = "/".join(map(str, e.path)) or "<root>"
            raise ValueError(f"payload schema validation failed: {e.message} at {path}")

    async def _reply_json(
        self,
        subject: str,
        obj: dict,
        rm: Optional[ReceivedMessage],
        corr_id: Optional[str] = None,
    ) -> None:
        corr = corr_id or (rm.correlation_id if rm else None)
        self.log.debug("reply_json", extra={
            "subject": subject,
            "corr": corr,
            "keys": sorted(list(obj.keys()))
        })
        msg = BusMessage.from_json(
            subject,
            obj,
            sender="ai-gateway",
            correlation_id=corr,
            ensure_trace=True,
            compress=getattr(self.cfg, "compress_outbound", False),
        )
        await self.bus.publish(msg)

    # -------------------------------------------------------------------------
    # LLM orchestration + prompts
    # -------------------------------------------------------------------------
    async def _llm_plan(self, cmd: str, args: dict, mapping: CommandMapping) -> LlmPlan:
        prompt = self._build_plan_prompt(cmd, args, mapping)
        self.log.debug("llm_plan_call", extra={
            "cmd": cmd, "prompt_chars": len(prompt)
        })
        obj = await self._llm_json(
            system=self.cfg.llm_system_prompt,
            prompt=prompt,
            required_keys={"action", "subject", "payload"},
            enforce_action="send_request",
            max_retries=self.cfg.llm_max_retries,
        )
        self.log.debug("llm_plan_ok", extra={
            "action": obj.get("action"), "subject": obj.get("subject")
        })

        if mapping.request_schema and obj.get("subject") == mapping.request_subject:
            self._validate_payload(obj.get("payload", {}), mapping.request_schema)

        ability = self.abilities.get_by_subject(str(obj.get("subject", "")))
        if ability and ability.payload_schema:
            self._validate_payload(obj.get("payload", {}), ability.payload_schema)

        return LlmPlan.from_json(obj)

    async def _llm_iterate(self, original_command: str, observation: dict):
        prompt = self._build_iterative_prompt(original_command, observation)
        self.log.debug("llm_iterate_call", extra={"prompt_chars": len(prompt)})
        obj = await self._llm_json(
            system=getattr(self.cfg, "llm_iterative_system_prompt", ""),
            prompt=prompt,
            required_keys={"action"},
            max_retries=getattr(self.cfg, "llm_max_retries", 2),
        )
        self.log.debug("llm_iterate_ok", extra={"action": obj.get("action")})
        action = str(obj.get("action"))
        if action == "send_request":
            ability = self.abilities.get_by_subject(str(obj.get("subject", "")))
            if ability and ability.payload_schema:
                self._validate_payload(obj.get("payload", {}), ability.payload_schema)
            return LlmPlan.from_json(obj)
        if action == "final_reply":
            return FinalReply.from_json(obj)
        raise ValueError(f"Unknown action in iterative decision: {action}")

    async def _llm_json(
            self,
            *,
            system: str,
            prompt: str,
            required_keys: Optional[Set[str]] = None,
            enforce_action: Optional[str] = None,
            max_retries: int = 2,
    ) -> dict:
        if len(prompt) > self.cfg.max_prompt_chars:
            prompt = prompt[: self.cfg.max_prompt_chars]

        last_error: Optional[str] = None
        cur_prompt = prompt
        for attempt in range(max_retries + 1):
            text = await self.llm_call(cur_prompt, system)
            try:
                obj = json.loads(self._extract_first_json(text))
                if required_keys and not required_keys.issubset(set(obj.keys())):
                    missing = sorted(list(required_keys - set(obj.keys())))
                    raise ValueError(f"missing keys: {', '.join(missing)}")
                if enforce_action is not None:
                    got = str(obj.get("action"))
                    if got != enforce_action:
                        raise ValueError(f"action must be '{enforce_action}', got '{got}'")
                self.log.debug("llm_json_success", extra={
                    "attempt": attempt, "keys": sorted(list(obj.keys())), "action": obj.get("action")
                })
                return obj
            except Exception as e:
                last_error = str(e)
                self.log.debug("llm_json_retry", extra={"attempt": attempt, "error": last_error})
                hint = (
                    f'Output exactly one JSON object. The "action" MUST be "{enforce_action}". '
                    "Follow the payload schema strictly; do not write final_reply at this stage."
                    if enforce_action else
                    "Output exactly one valid JSON object per the schema."
                )
                cur_prompt = f"{prompt}\nCorrection: {hint}"
        raise RuntimeError(f"LLM did not return valid JSON after retries: {last_error}")

    def _build_plan_prompt(self, cmd: str, args: dict, mapping: CommandMapping) -> str:
        contract = {
            "request_subject": mapping.request_subject,
            "response_subject": mapping.response_subject,
            "payload_schema": mapping.request_schema or {},
            "example_payload": mapping.example_payload or {},
        }
        abilities = self.abilities.as_contract()
        instructions = mapping.llm_instructions or ""
        context = {
            "command": cmd,
            "args": args,
            "default_request_subject": mapping.request_subject,
            "default_response_subject": mapping.response_subject,
        }
        return (
                "You are planning the FIRST action for a task. Output only one JSON object.\n"
                'Allowed keys: action, subject, payload, await_response, response_subject (optional).\n'
                "Rules:\n"
                '- For the first step, the action MUST be "send_request". Never return "final_reply" here.\n'
                "- subject MUST be one of the abilities' request_subjects or the contract request_subject.\n"
                "- payload MUST satisfy the payload_schema when provided.\n"
                "- Set await_response true for calls with response_subject.\n"
                "Abilities: " + json.dumps(abilities, ensure_ascii=False) + "\n"
                "Contract: " + json.dumps(contract,ensure_ascii=False) + "\n"
                "Additional instructions: " + instructions + "\n"
                "Context: " + json.dumps(context, ensure_ascii=False)
        )

    def _build_iterative_prompt(self, original_command: str, observation: dict) -> str:
        abilities = self.abilities.as_contract()
        return (
            "Plan next step based on the latest observation. If you have enough information to conclude for the human, "
            'return {"action":"final_reply","result":{...}}; otherwise return a {"action":"send_request",...}.\n'
            f"Abilities: {json.dumps(abilities, ensure_ascii=False)}\n"
            f"Original command: {original_command}\n"
            f"Observation: {json.dumps(observation, ensure_ascii=False)}"
        )

    @staticmethod
    def _extract_first_json(text: str) -> str:
        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON object found in LLM output")
        depth = 0
        for i in range(start, len(text)):
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
        raise ValueError("Unterminated JSON object in LLM output")
