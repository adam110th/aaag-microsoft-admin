"""Tests for src.core.auth."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from tests.conftest import make_env

# Fake JWT: header.payload.signature — payload is {"roles": ["Chat.Read.All"]}
# We just need a token with three dot-separated parts for decode diagnostics.
FAKE_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJyb2xlcyI6WyJDaGF0LlJlYWQuQWxsIl19.sig"


class TestGetClientCredentialsToken:
    @patch("src.core.auth.msal.ConfidentialClientApplication")
    def test_success(self, mock_cca: MagicMock) -> None:
        from src.core.auth import get_client_credentials_token

        instance = mock_cca.return_value
        instance.acquire_token_for_client.return_value = {"access_token": FAKE_TOKEN}

        token = get_client_credentials_token(make_env())
        assert token == FAKE_TOKEN
        instance.acquire_token_for_client.assert_called_once()

    @patch("src.core.auth.msal.ConfidentialClientApplication")
    def test_failure_exits(self, mock_cca: MagicMock) -> None:
        from src.core.auth import get_client_credentials_token

        instance = mock_cca.return_value
        instance.acquire_token_for_client.return_value = {"error": "invalid_client"}

        with pytest.raises(SystemExit):
            get_client_credentials_token(make_env())


class TestGetDelegatedToken:
    @patch("src.core.auth._save_token_cache")
    @patch("src.core.auth._load_token_cache")
    @patch("src.core.auth.msal.PublicClientApplication")
    def test_silent_success(
        self, mock_pca: MagicMock, mock_load: MagicMock, mock_save: MagicMock
    ) -> None:
        from src.core.auth import get_delegated_token

        mock_load.return_value = MagicMock()
        instance = mock_pca.return_value
        instance.get_accounts.return_value = [{"username": "user@test.com"}]
        instance.acquire_token_silent.return_value = {"access_token": FAKE_TOKEN}

        token = get_delegated_token(make_env(), ["User.Read"])
        assert token == FAKE_TOKEN
        instance.acquire_token_interactive.assert_not_called()

    @patch("src.core.auth._save_token_cache")
    @patch("src.core.auth._load_token_cache")
    @patch("src.core.auth.msal.PublicClientApplication")
    def test_interactive_fallback(
        self, mock_pca: MagicMock, mock_load: MagicMock, mock_save: MagicMock
    ) -> None:
        from src.core.auth import get_delegated_token

        mock_load.return_value = MagicMock()
        instance = mock_pca.return_value
        instance.get_accounts.return_value = []
        instance.acquire_token_interactive.return_value = {"access_token": FAKE_TOKEN}

        token = get_delegated_token(make_env(), ["User.Read"])
        assert token == FAKE_TOKEN
        instance.acquire_token_interactive.assert_called_once()

    @patch("src.core.auth._save_token_cache")
    @patch("src.core.auth._load_token_cache")
    @patch("src.core.auth.msal.PublicClientApplication")
    def test_interactive_failure_exits(
        self, mock_pca: MagicMock, mock_load: MagicMock, mock_save: MagicMock
    ) -> None:
        from src.core.auth import get_delegated_token

        mock_load.return_value = MagicMock()
        instance = mock_pca.return_value
        instance.get_accounts.return_value = []
        instance.acquire_token_interactive.return_value = {"error": "user_cancelled"}

        with pytest.raises(SystemExit):
            get_delegated_token(make_env(), ["User.Read"])
