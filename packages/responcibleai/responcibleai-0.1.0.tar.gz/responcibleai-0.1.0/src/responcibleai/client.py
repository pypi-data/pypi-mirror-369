# src/responcibleai/client.py
from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

import requests
from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .__about__ import __version__
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ResponcibleAIError,
    ServerError,
)

DEFAULT_BASE_URL = "https://api.responcibleai.com"


class CloakClient:
    """
    Minimal SDK client for ResponcibleAI's /redact_pii endpoint.

    Example:
        from responcibleai import CloakClient
        client = CloakClient(api_key="YOUR_TOKEN")
        out = client.redact_pii(
            "Michael Chang (Phone: +1-202-555-0198, Email: michael.chang@intel.com) "
            "has submitted PAN: MCHCH4321F and Aadhar: 4444 5555 6666"
        )
        print(out["modified"])
        # => "{Person} (Phone: {PHONE_NUMBER}, Email: {EMAIL_ADDRESS}) has submitted PAN: {PAN} and Aadhar: {AADHAAR}"
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 0.5,
        status_forcelist: Tuple[int, ...] = (408, 429, 500, 502, 503, 504),
        session: Optional[Session] = None,
        user_agent: Optional[str] = None,
        proxies: Optional[Dict[str, str]] = None,
    ) -> None:
        self.api_key = api_key or os.getenv("RESPONCIBLEAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key missing. Set RESPONCIBLEAI_API_KEY or pass api_key=.")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent or f"responcibleai-sdk/{__version__}"
        self.proxies = dict(proxies) if proxies else None

        self._session = session or requests.Session()
        self._install_retries(self._session, retries, backoff_factor, status_forcelist)

    # -------------------- Public API --------------------

    def redact_pii(self, text: str) -> Dict[str, Any]:
        """
        Call POST /redact_pii with a text string.
        Returns a dict like: {"original": "...", "modified": "..."}.
        """
        return self._request_json("POST", "/redact_pii", json={"text": text})

    # Back-compat alias if you previously called client.mask(...)
    def mask(self, text: str) -> Dict[str, Any]:
        """Alias for redact_pii(text)."""
        return self.redact_pii(text)

    # ---------------- Context Manager ------------------

    def close(self) -> None:
        if self._session:
            self._session.close()

    def __enter__(self) -> "CloakClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ------------------ Internals ----------------------

    def _install_retries(
        self,
        session: Session,
        retries: int,
        backoff_factor: float,
        status_forcelist: Tuple[int, ...],
    ) -> None:
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            status=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            allowed_methods=frozenset(["GET", "POST"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
        }

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def _request_json(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = self._url(path)
        try:
            resp = self._session.request(
                method,
                url,
                headers=self._headers(),
                timeout=self.timeout,
                proxies=self.proxies,
                **kwargs,
            )
        except requests.RequestException as e:
            # Network, DNS, TLS, timeout, etc.
            raise NetworkError(str(e)) from e

        self._raise_for_status(resp)
        return self._parse_json(resp)

    @staticmethod
    def _parse_json(resp: Response) -> Dict[str, Any]:
        try:
            return resp.json()  # type: ignore[return-value]
        except ValueError as e:
            raise ServerError(f"Invalid JSON from server: {resp.text[:200]}") from e

    def _raise_for_status(self, resp: Response) -> None:
        if 200 <= resp.status_code < 300:
            return

        status = resp.status_code
        msg = self._extract_error_message(resp) or (resp.text[:500] if resp.text else f"HTTP {status}")

        if status == 400:
            raise BadRequestError(msg)
        if status == 401:
            raise AuthenticationError(msg)
        if status == 403:
            raise AuthorizationError(msg)
        if status == 404:
            raise NotFoundError(msg)
        if status == 429:
            ra = resp.headers.get("Retry-After")
            detail = f"Rate limit exceeded. Retry-After: {ra}s" if ra else "Rate limit exceeded."
            raise RateLimitError(detail)
        if 500 <= status < 600:
            raise ServerError(msg)

        raise ResponcibleAIError(msg)

    @staticmethod
    def _extract_error_message(resp: Response) -> Optional[str]:
        """
        Tries common error shapes such as:
          {"error": {"message": "..."}}
          {"message": "..."}
        """
        try:
            data = resp.json()
        except ValueError:
            return None

        if isinstance(data, dict):
            err = data.get("error")
            if isinstance(err, dict):
                return err.get("message") or err.get("detail")
            if isinstance(data.get("message"), str):
                return data["message"]
        return None
