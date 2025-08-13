# receiptkit

Signed, policy-evaluated receipts for LLM calls. Privacy-preserving (hashes only), tamper-evident (HMAC), and CI-friendly.

## Quick start
```python
from receiptkit import ReceiptManager

rm = ReceiptManager(enabled=True, receipts_dir="receipts", policies_path="policies.yaml")
# Call your LLM...
rm.write_receipt(
  model="your-model",
  params={"temperature": 0.2},
  prompt_text="...",
  response_text="...",
  latency_ms=120,
  context_key="feature-name"
)
```

## Policies
Define guardrails in policies.yaml (PII, jailbreak, citation, topics). Receipts include pass/fail per rule.

## Signing
Set RECEIPT_SECRET to add an HMAC signature to each receipt.
