"""1151 Python SDK.

This package exposes a minimal API client with an ``exchange`` method.

Usage:

    from m1151 import Client
    client = Client(api_key="...")
    client.exchange(amount=1.0, in_return="BTC", you_give="ETH", receive_wallet="...")
"""

from __future__ import annotations

from .client import Client

__all__ = ["Client"]

__version__ = "0.1.0"
