from __future__ import annotations

from typing import Any, Dict

import requests


DEFAULT_BASE_URL = "https://api.1151.to"


class ExchangeResponse:
    """Response object for exchange operations."""
    
    def __init__(self, response_data: Dict[str, Any]) -> None:
        self._data = response_data
        
    @property
    def amount(self) -> float:
        """The exchange amount."""
        return float(self._data.get('amount', 0))
    
    @property
    def id(self) -> float:
        """The exchange amount."""
        return float(self._data.get('id', -1))
    
    @property
    def wallet_to(self) -> str:
        """The destination wallet address."""
        return str(self._data.get('wallet_to', ''))
    
    @property
    def raw_data(self) -> Dict[str, Any]:
        """Access to the raw response data."""
        return self._data.copy()
    
    def __repr__(self) -> str:
        return f"ExchangeResponse(amount={self.amount}, wallet_to='{self.wallet_to}')"


class Client:

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        *,
        timeout: float | None = 30,
        session: requests.Session | None = None,
    ) -> None:
        if not isinstance(api_key, str) or not api_key:
            raise ValueError("api_key must be a non-empty string")
        self.api_key = api_key
        self.base_url = base_url or DEFAULT_BASE_URL
        self.timeout = timeout
        self.session = session or requests.Session()

    def _url(self, path: str) -> str:
        if not self.base_url:
            raise ValueError("base_url is not set. Pass base_url to Client(...)")
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def exchange(
        self,
        *,
        amount: float,
        in_return: str,
        you_give: str,
        receive_wallet: str,
        extra: Dict[str, Any] | None = None,
    ) -> ExchangeResponse:

        if not isinstance(amount, (int, float)):
            raise TypeError("amount must be a number")
        payload: Dict[str, Any] = {
            "api_key": self.api_key,
            "amount": float(amount),
            "in_return": in_return,
            "you_give": you_give,
            "receive_wallet": receive_wallet,
        }
        if extra:
            payload.update(extra)

        url = self._url("/exchange")
        resp = self.session.post(url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return ExchangeResponse(resp.json())