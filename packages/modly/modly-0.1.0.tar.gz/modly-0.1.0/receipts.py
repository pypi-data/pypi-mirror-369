from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

try:
    from jsonschema import validate as js_validate  # optional
except Exception:  # pragma: no cover
    js_validate = None  # type: ignore

try:
    # Local policy tools (lightweight regex/substring checks)
    from policy_tools import PIITool, JailbreakTool, CitationTool, TopicsTool, IntentTool
except Exception:
    # Fallback no-op tools if policy_tools is absent
    @dataclass
    class _Res:
        status: str
        details: dict | None = None

    class PIITool:  # type: ignore
        def __init__(self, enabled: bool = False):
            self.enabled = enabled
        def check(self, text: str) -> _Res:
            return _Res("skip" if not self.enabled else "pass")

    class JailbreakTool:  # type: ignore
        def __init__(self, patterns: list[str] | None = None):
            self.patterns = patterns or []
        def check(self, text: str) -> _Res:
            return _Res("skip" if not self.patterns else "pass")

    class CitationTool:  # type: ignore
        def __init__(self, require: bool = False):
            self.require = require
        def check(self, text: str) -> _Res:
            return _Res("skip" if not self.require else "pass")

    class TopicsTool:  # type: ignore
        def __init__(self, disallowed_topics: list[str] | None = None):
            self.disallowed_topics = disallowed_topics or []
        def check(self, text: str) -> _Res:
            return _Res("skip" if not self.disallowed_topics else "pass")

    class IntentTool:  # type: ignore
        def check_intent(self, *, prompt_text: str, baseline_intent: str) -> _Res:
            return _Res("skip")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class Policies:
    require_no_pii: bool = False
    disallow_topics: Optional[list[str]] = None
    require_citation: bool = False
    jailbreak_patterns: Optional[list[str]] = None

    @staticmethod
    def from_yaml(path: Optional[str]) -> "Policies":
        if not path:
            return Policies()
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        return Policies(
            require_no_pii=bool(data.get("require_no_pii", False)),
            disallow_topics=list(data.get("disallow_topics", []) or []),
            require_citation=bool(data.get("require_citation", False)),
            jailbreak_patterns=list(data.get("jailbreak_patterns", []) or []),
        )


class ReceiptManager:
    def __init__(
        self,
        enabled: bool,
        receipts_dir: str,
        policies_path: Optional[str] = None,
        baseline_file: Optional[str] = None,
        secret_env: str = "RECEIPT_SECRET",
    ) -> None:
        self.enabled = enabled
        self.receipts_path = Path(receipts_dir) if receipts_dir else Path("./receipts")
        self.receipts_path.mkdir(parents=True, exist_ok=True)
        self.policies = Policies.from_yaml(policies_path)
        # Initialize policy tools (lightweight)
        self._pii_tool = PIITool(enabled=self.policies.require_no_pii)
        self._jailbreak_tool = JailbreakTool(patterns=self.policies.jailbreak_patterns or [])
        self._citation_tool = CitationTool(require=self.policies.require_citation)
        self._topics_tool = TopicsTool(disallowed_topics=self.policies.disallow_topics or [])
        self._intent_tool = IntentTool()
        self.baseline = {}
        if baseline_file and Path(baseline_file).exists():
            try:
                self.baseline = json.loads(Path(baseline_file).read_text(encoding="utf-8"))
            except Exception:
                self.baseline = {}
        self.secret = os.getenv(secret_env, "")

    def _evaluate_policies(self, text: str) -> Dict[str, Any]:
        results: Dict[str, Any] = {"pii": "skip", "jailbreak": "skip", "citation": "skip"}
        # PII
        try:
            pii_res = self._pii_tool.check(text)
            if pii_res.status != "skip":
                results["pii"] = pii_res.status
        except Exception:
            pass
        # Jailbreak
        try:
            jb_res = self._jailbreak_tool.check(text)
            if jb_res.status != "skip":
                results["jailbreak"] = jb_res.status
        except Exception:
            pass
        # Citation
        try:
            cit_res = self._citation_tool.check(text)
            if cit_res.status != "skip":
                results["citation"] = cit_res.status
        except Exception:
            pass
        # Topics
        try:
            topics_res = self._topics_tool.check(text)
            if getattr(topics_res, "status", "skip") != "skip":
                details = getattr(topics_res, "details", {}) or {}
                disallowed = details.get("disallowed", [])
                results["topics"] = {"disallowed": disallowed, "status": topics_res.status}
        except Exception:
            pass
        return results

    def _drift(self, context_key: str, prompt_hash: str) -> Dict[str, Any]:
        baseline_hash = None
        if isinstance(self.baseline, dict):
            baseline_hash = self.baseline.get(context_key) or self.baseline.get("prompt_hash")
        return {"prompt_hash_changed": bool(baseline_hash and baseline_hash != prompt_hash), "baseline": baseline_hash}

    def _sign(self, payload: bytes) -> str:
        if not self.secret:
            return ""
        mac = hmac.new(self.secret.encode("utf-8"), payload, hashlib.sha256).digest()
        return base64.b64encode(mac).decode("ascii")

    def write_receipt(
        self,
        *,
        model: str,
        params: Dict[str, Any],
        prompt_text: str,
        response_text: str,
        latency_ms: int,
        context_key: str = "default",
        usage: Optional[Dict[str, Any]] = None,
        cost: Optional[float] = None,
        session_id: Optional[str] = None,
    ) -> None:
        if not self.enabled:
            return
        req_hash = sha256_hex(prompt_text.encode("utf-8"))
        res_hash = sha256_hex((response_text or "").encode("utf-8"))
        guard = self._evaluate_policies(response_text or "")
        # Intent check if baseline has an intent description under key f"{context_key}:intent"
        baseline_intent = None
        if isinstance(self.baseline, dict):
            baseline_intent = self.baseline.get(f"{context_key}:intent") or self.baseline.get("intent")
        if baseline_intent:
            try:
                intent_result = self._intent_tool.check_intent(prompt_text=prompt_text, baseline_intent=baseline_intent)
                guard["intent"] = getattr(intent_result, "status", "skip")
            except Exception:
                pass
        drift = self._drift(context_key, req_hash)
        ts = int(time.time())
        short = res_hash[:8]
        receipt_id = f"receipt_{ts}_{short}"
        receipt = {
            "schema_version": "1.0.0",
            "receipt_id": receipt_id,
            "request_fingerprint": req_hash,
            "response_fingerprint": res_hash,
            "model": model,
            "params": params,
            "guardrails": guard,
            "drift": drift,
            "context": context_key,
            "grounding": {"mode": "none"},
            "usage": usage,
            "cost": cost,
            "latency_ms": latency_ms,
            "signed_at": now_iso(),
            "session_id": session_id,
        }
        # Validate against bundled schema (best-effort)
        try:
            if js_validate is not None:
                schema_path = Path(__file__).with_name("receipts_schema.json")
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                js_validate(instance=receipt, schema=schema)
        except Exception:
            pass
        payload = json.dumps(receipt, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        sig = self._sign(payload)
        receipt["signature"] = sig
        out = self.receipts_path / f"{receipt_id}.json"
        out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")

