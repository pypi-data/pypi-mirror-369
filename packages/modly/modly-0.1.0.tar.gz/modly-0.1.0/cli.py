from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import ReceiptManager


def _load_receipts(receipts_dir: str):
    p = Path(receipts_dir)
    if not p.exists():
        return []
    out = []
    for f in sorted(p.glob("*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out


def _summarize(receipts: list[dict]) -> dict:
    guards = [r.get("guardrails", {}) for r in receipts]
    summary: dict[str, dict[str, int]] = {}
    for g in guards:
        for key in ("pii", "jailbreak", "citation"):
            val = g.get(key, "skip")
            summary.setdefault(key, {})[val] = summary.get(key, {}).get(val, 0) + 1
        topics = g.get("topics")
        tstat = topics.get("status", "skip") if isinstance(topics, dict) else "skip"
        summary.setdefault("topics", {})[tstat] = summary.get("topics", {}).get(tstat, 0) + 1
        intent = g.get("intent", "skip")
        summary.setdefault("intent", {})[intent] = summary.get("intent", {}).get(intent, 0) + 1
    return summary


def _stats(receipts: list[dict]) -> dict:
    by_model: dict[str, int] = {}
    by_context: dict[str, int] = {}
    for r in receipts:
        m = r.get("model", "unknown")
        c = r.get("context", "unknown")
        by_model[m] = by_model.get(m, 0) + 1
        by_context[c] = by_context.get(c, 0) + 1
    return {"model": by_model, "context": by_context}


def cmd_generate(args: argparse.Namespace) -> int:
    mgr = ReceiptManager(
        enabled=True,
        receipts_dir=args.receipts_dir,
        policies_path=args.policies,
        baseline_file=args.baseline,
    )
    prompt = Path(args.prompt).read_text(encoding="utf-8") if Path(args.prompt).exists() else args.prompt
    response = Path(args.response).read_text(encoding="utf-8") if Path(args.response).exists() else args.response
    mgr.write_receipt(
        model=args.model,
        params={},
        prompt_text=prompt,
        response_text=response,
        latency_ms=args.latency_ms,
        context_key=args.context,
    )
    print(f"Wrote receipt to {args.receipts_dir}")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    rcpts = _load_receipts(args.receipts_dir)
    s = _summarize(rcpts) if args.mode == "summary" else _stats(rcpts)
    out = json.dumps(s, indent=2) if args.format == "json" else str(s)
    print(out)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="receiptkit", description="Receipts toolkit")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="Generate a receipt from prompt/response")
    g.add_argument("--model", required=True)
    g.add_argument("--prompt", required=True, help="Prompt text or file path")
    g.add_argument("--response", required=True, help="Response text or file path")
    g.add_argument("--receipts-dir", default="receipts")
    g.add_argument("--policies")
    g.add_argument("--baseline")
    g.add_argument("--context", default="default")
    g.add_argument("--latency-ms", type=int, default=0)
    g.set_defaults(func=cmd_generate)

    a = sub.add_parser("audit", help="Audit receipts directory")
    a.add_argument("--receipts-dir", default="receipts")
    a.add_argument("--mode", choices=["summary", "stats"], default="summary")
    a.add_argument("--format", choices=["json", "print"], default="json")
    a.set_defaults(func=cmd_audit)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

