"""GraphClient — thin wrapper around Microsoft Graph HTTP calls with retry and pagination."""

from __future__ import annotations

import json
import time

import requests

from src.core.config import MAX_RETRIES, REQUEST_TIMEOUT


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class GraphAPIError(Exception):
    """Base exception for Graph API errors with structured detail."""

    def __init__(self, message: str, status_code: int, code: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class GraphPermissionError(GraphAPIError):
    """Raised when Graph API returns 403 due to insufficient permissions."""


class TenantMismatchError(GraphAPIError):
    """Raised when Graph API returns 403 due to cross-tenant access."""


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class GraphClient:
    """Binds a token and provides ``get()``, ``post()``, ``patch()``, ``delete()``, ``get_paged()``."""

    def __init__(self, token: str) -> None:
        self.token = token

    # -- low-level ---------------------------------------------------------

    def _request(
        self,
        method: str,
        url: str,
        *,
        timeout: int = REQUEST_TIMEOUT,
        stream: bool = False,
        headers_extra: dict[str, str] | None = None,
        json_body: dict | list | None = None,
    ) -> requests.Response:
        """Execute an HTTP request with exponential backoff for 429 / 5xx."""
        headers: dict[str, str] = {"Authorization": f"Bearer {self.token}"}
        if json_body is not None:
            headers["Content-Type"] = "application/json"
        if headers_extra:
            headers.update(headers_extra)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = requests.request(
                    method,
                    url,
                    headers=headers,
                    timeout=timeout,
                    stream=stream,
                    json=json_body,
                )
            except requests.exceptions.Timeout:
                print(f"  Timeout on attempt {attempt}/{MAX_RETRIES}: {url}")
                if attempt == MAX_RETRIES:
                    raise
                time.sleep(2**attempt)
                continue

            if resp.status_code == 429 or resp.status_code >= 500:
                retry_after = int(resp.headers.get("Retry-After", 2**attempt))
                print(
                    f"  HTTP {resp.status_code} on attempt {attempt}/{MAX_RETRIES}, "
                    f"retrying in {retry_after}s ..."
                )
                if attempt == MAX_RETRIES:
                    resp.raise_for_status()
                time.sleep(retry_after)
                continue

            if resp.status_code >= 400:
                self._handle_error(resp)

            return resp

        raise RuntimeError("Max retries exhausted")  # unreachable

    def _handle_error(self, resp: requests.Response) -> None:
        """Parse Graph API error body, detect tenant mismatch, and raise."""
        try:
            err_body = resp.json()
            err_obj = err_body.get("error", {})
            err_msg = err_obj.get("message", resp.text[:500])
            err_code = err_obj.get("code", "")
            err_inner = err_obj.get("innerError", {})
        except Exception:
            err_msg = resp.text[:500]
            err_code = ""
            err_inner = {}

        print(f"  HTTP {resp.status_code}: {err_code}")
        print(f"  Message: {err_msg}")
        if err_inner:
            print(f"  Inner error: {json.dumps(err_inner, indent=4)}")

        # Detect specific 403 sub-types
        inner_msg = err_inner.get("message", "") if isinstance(err_inner, dict) else ""
        combined = f"{err_msg} {inner_msg}".lower()
        if resp.status_code == 403:
            if "tenant id mismatch" in combined:
                raise TenantMismatchError(err_msg, 403, err_code)
            raise GraphPermissionError(err_msg, 403, err_code)

        resp.raise_for_status()

    # -- public API --------------------------------------------------------

    def get(
        self,
        url: str,
        *,
        timeout: int = REQUEST_TIMEOUT,
        stream: bool = False,
        headers_extra: dict[str, str] | None = None,
    ) -> requests.Response:
        """HTTP GET with retry."""
        return self._request(
            "GET", url, timeout=timeout, stream=stream, headers_extra=headers_extra,
        )

    def post(
        self,
        url: str,
        *,
        json_body: dict | list | None = None,
        timeout: int = REQUEST_TIMEOUT,
    ) -> requests.Response:
        """HTTP POST with retry."""
        return self._request("POST", url, json_body=json_body, timeout=timeout)

    def patch(
        self,
        url: str,
        *,
        json_body: dict | list | None = None,
        timeout: int = REQUEST_TIMEOUT,
    ) -> requests.Response:
        """HTTP PATCH with retry."""
        return self._request("PATCH", url, json_body=json_body, timeout=timeout)

    def delete(self, url: str, *, timeout: int = REQUEST_TIMEOUT) -> requests.Response:
        """HTTP DELETE with retry."""
        return self._request("DELETE", url, timeout=timeout)

    def get_paged(
        self,
        url: str,
        *,
        timeout: int = REQUEST_TIMEOUT,
        page_label: str = "items",
    ) -> list[dict]:
        """Follow ``@odata.nextLink`` pagination and return all items."""
        items: list[dict] = []
        page = 0
        while url:
            page += 1
            print(f"  Fetching {page_label} page {page} ...")
            resp = self.get(url, timeout=timeout)
            data = resp.json()
            items.extend(data.get("value", []))
            url = data.get("@odata.nextLink", "")
        return items
