"""Authentication helpers for Microsoft Graph API."""

from __future__ import annotations

import base64
import json
import sys

import msal

from src.core.config import TOKEN_CACHE_PATH

# ---------------------------------------------------------------------------
# Token cache persistence
# ---------------------------------------------------------------------------


def _load_token_cache() -> msal.SerializableTokenCache:
    """Load MSAL token cache from disk, or return empty cache."""
    cache = msal.SerializableTokenCache()
    if TOKEN_CACHE_PATH.exists():
        cache.deserialize(TOKEN_CACHE_PATH.read_text(encoding="utf-8"))
    return cache


def _save_token_cache(cache: msal.SerializableTokenCache) -> None:
    """Persist MSAL token cache to disk if it changed."""
    if cache.has_state_changed:
        TOKEN_CACHE_PATH.write_text(cache.serialize(), encoding="utf-8")


# ---------------------------------------------------------------------------
# Client credentials (application permissions)
# ---------------------------------------------------------------------------


def get_client_credentials_token(
    env: dict[str, str],
    scopes: list[str] | None = None,
) -> str:
    """Acquire an OAuth2 token via MSAL client-credentials flow.

    Parameters
    ----------
    env:
        Must contain ``AZURE_TENANT_ID``, ``AZURE_CLIENT_ID``, and
        ``AZURE_CLIENT_SECRET``.
    scopes:
        OAuth2 scopes. Defaults to ``["https://graph.microsoft.com/.default"]``.
    """
    if scopes is None:
        scopes = ["https://graph.microsoft.com/.default"]

    authority = f"https://login.microsoftonline.com/{env['AZURE_TENANT_ID']}"
    app = msal.ConfidentialClientApplication(
        env["AZURE_CLIENT_ID"],
        authority=authority,
        client_credential=env["AZURE_CLIENT_SECRET"],
    )
    result = app.acquire_token_for_client(scopes=scopes)
    if "access_token" not in result:
        error = result.get("error_description", result.get("error", "unknown error"))
        print(f"ERROR: Failed to acquire access token: {error}")
        sys.exit(1)

    token: str = result["access_token"]

    # Decode JWT payload to show granted roles (for diagnostics)
    try:
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        roles = payload.get("roles", [])
        print(f"  Token roles: {roles}")
    except Exception:
        pass  # Token decode is best-effort diagnostics

    return token


# ---------------------------------------------------------------------------
# Delegated (interactive browser)
# ---------------------------------------------------------------------------


def get_delegated_token(
    env: dict[str, str],
    scopes: list[str] | None = None,
) -> str:
    """Acquire an OAuth2 token via interactive browser login (delegated permissions).

    Parameters
    ----------
    env:
        Must contain ``AZURE_TENANT_ID`` and ``AZURE_CLIENT_ID``.
    scopes:
        Delegated permission scopes. Defaults to
        ``["Chat.Read", "Chat.ReadBasic", "User.Read"]``.
    """
    if scopes is None:
        scopes = ["Chat.Read", "Chat.ReadBasic", "User.Read"]

    authority = f"https://login.microsoftonline.com/{env['AZURE_TENANT_ID']}"
    cache = _load_token_cache()

    app = msal.PublicClientApplication(
        env["AZURE_CLIENT_ID"],
        authority=authority,
        token_cache=cache,
    )

    # Try silent acquisition first (uses cached refresh token)
    accounts = app.get_accounts()
    if accounts:
        print("  Found cached account, attempting silent token acquisition ...")
        result = app.acquire_token_silent(scopes, account=accounts[0])
        if result and "access_token" in result:
            _save_token_cache(cache)
            print("  Token acquired silently (cached credentials).")
            return result["access_token"]

    # Interactive browser login
    print("\n  Opening browser for sign-in ...")
    try:
        result = app.acquire_token_interactive(
            scopes=scopes,
            prompt="select_account",
        )
    except Exception as exc:
        print(f"ERROR: Interactive authentication failed: {exc}")
        print(
            "\nEnsure your Azure app registration has:\n"
            "  1. Authentication > Add platform > Mobile and desktop applications\n"
            "     Add redirect URI: http://localhost\n"
            "  2. Authentication > Allow public client flows = Yes\n"
            "  3. API permissions > Delegated > required scopes (with admin or user consent)\n"
        )
        sys.exit(1)

    if not result or "access_token" not in result:
        error = ""
        if result:
            error = result.get("error_description", result.get("error", "unknown error"))
        print(f"ERROR: Interactive authentication failed: {error}")
        sys.exit(1)

    _save_token_cache(cache)
    print("  Authenticated via browser sign-in.")
    return result["access_token"]
