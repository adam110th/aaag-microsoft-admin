"""Tests for src.core.config."""

from __future__ import annotations

import pytest

from src.core.config import load_environment


class TestLoadEnvironment:
    def test_missing_vars_exits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("AZURE_TENANT_ID", raising=False)
        monkeypatch.delenv("AZURE_CLIENT_ID", raising=False)
        monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)
        monkeypatch.setattr("src.core.config.load_dotenv", lambda *a, **kw: None)
        with pytest.raises(SystemExit):
            load_environment()

    def test_valid_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.config.load_dotenv", lambda *a, **kw: None)
        monkeypatch.setenv("AZURE_TENANT_ID", "tid")
        monkeypatch.setenv("AZURE_CLIENT_ID", "cid")
        monkeypatch.setenv("AZURE_CLIENT_SECRET", "secret")
        env = load_environment()
        assert env["AZURE_TENANT_ID"] == "tid"

    def test_client_secret_optional(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.config.load_dotenv", lambda *a, **kw: None)
        monkeypatch.setenv("AZURE_TENANT_ID", "tid")
        monkeypatch.setenv("AZURE_CLIENT_ID", "cid")
        monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)
        env = load_environment()
        assert "AZURE_CLIENT_SECRET" not in env

    def test_extra_required_present(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.config.load_dotenv", lambda *a, **kw: None)
        monkeypatch.setenv("AZURE_TENANT_ID", "tid")
        monkeypatch.setenv("AZURE_CLIENT_ID", "cid")
        monkeypatch.setenv("MY_EXTRA", "val")
        env = load_environment(extra_required=("MY_EXTRA",))
        assert env["MY_EXTRA"] == "val"

    def test_extra_required_missing_exits(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.config.load_dotenv", lambda *a, **kw: None)
        monkeypatch.setenv("AZURE_TENANT_ID", "tid")
        monkeypatch.setenv("AZURE_CLIENT_ID", "cid")
        monkeypatch.delenv("MY_EXTRA", raising=False)
        with pytest.raises(SystemExit):
            load_environment(extra_required=("MY_EXTRA",))

    def test_extra_optional_loaded(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("src.core.config.load_dotenv", lambda *a, **kw: None)
        monkeypatch.setenv("AZURE_TENANT_ID", "tid")
        monkeypatch.setenv("AZURE_CLIENT_ID", "cid")
        monkeypatch.setenv("OPT_VAR", "val")
        env = load_environment(extra_optional=("OPT_VAR",))
        assert env["OPT_VAR"] == "val"
