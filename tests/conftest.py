"""Shared test fixtures."""

from __future__ import annotations

import pathlib

import pytest

FAKE_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.fake"
CHAT_ID = "19:test_chat_id@thread.v2"


@pytest.fixture()
def media_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    d = tmp_path / "media"
    d.mkdir()
    return d


def make_env(**overrides: str) -> dict[str, str]:
    """Return a minimal Azure AD environment dict."""
    base = {
        "AZURE_TENANT_ID": "test-tenant-id",
        "AZURE_CLIENT_ID": "test-client-id",
        "AZURE_CLIENT_SECRET": "test-secret",
    }
    base.update(overrides)
    return base
