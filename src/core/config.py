"""Shared configuration: environment loading and constants."""

from __future__ import annotations

import os
import pathlib
import sys

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
GRAPH_BETA = "https://graph.microsoft.com/beta"
TOKEN_CACHE_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / ".token_cache.bin"
REQUEST_TIMEOUT = 30   # seconds for normal API calls
DOWNLOAD_TIMEOUT = 60  # seconds for large file downloads
MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------


def load_environment(
    *,
    extra_required: tuple[str, ...] = (),
    extra_optional: tuple[str, ...] = (),
) -> dict[str, str]:
    """Load and validate Azure AD environment variables.

    Always requires ``AZURE_TENANT_ID`` and ``AZURE_CLIENT_ID``.
    ``AZURE_CLIENT_SECRET`` is always optional.

    Parameters
    ----------
    extra_required:
        Additional variable names that *must* be present.
    extra_optional:
        Additional variable names loaded if available.
    """
    env_path = pathlib.Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(env_path)

    required = ("AZURE_TENANT_ID", "AZURE_CLIENT_ID") + extra_required
    optional = ("AZURE_CLIENT_SECRET",) + extra_optional

    env: dict[str, str] = {}
    missing: list[str] = []

    for var in required:
        val = os.environ.get(var, "").strip()
        if not val:
            missing.append(var)
        else:
            env[var] = val

    for var in optional:
        val = os.environ.get(var, "").strip()
        if val:
            env[var] = val

    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        print("Set them in .env or export them before running this script.")
        sys.exit(1)

    return env
