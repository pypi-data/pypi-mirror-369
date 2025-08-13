"""
receiptkit: signed provenance receipts for LLM calls.

Usage:
    from receiptkit import ReceiptManager, Policies
"""

from .receipts import ReceiptManager, Policies

__version__ = "0.1.0"

__all__ = ["ReceiptManager", "Policies"]

