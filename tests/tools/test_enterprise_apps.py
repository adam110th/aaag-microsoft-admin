"""Tests for src.tools.enterprise_apps."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
import responses

from src.core.config import GRAPH_BASE
from src.core.graph_client import GraphClient
from src.tools.enterprise_apps.tool import (
    compute_cert_status,
    delete_apps,
    display_list_table,
    fetch_all_service_principals,
    fetch_assignments_count,
    show_app_details,
)
from tests.conftest import FAKE_TOKEN, make_env


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_sp(
    sp_id: str = "sp-1",
    name: str = "Test App",
    enabled: bool = True,
    key_credentials: list | None = None,
) -> dict:
    return {
        "id": sp_id,
        "appId": f"app-{sp_id}",
        "displayName": name,
        "createdDateTime": "2025-01-01T00:00:00Z",
        "accountEnabled": enabled,
        "keyCredentials": key_credentials or [],
        "servicePrincipalType": "Application",
    }


# ---------------------------------------------------------------------------
# compute_cert_status
# ---------------------------------------------------------------------------


class TestComputeCertStatus:
    def test_no_credentials(self) -> None:
        status, expiry = compute_cert_status([])
        assert status == "None"
        assert expiry == "---"

    def test_valid_cert(self) -> None:
        future = (datetime.now(tz=timezone.utc) + timedelta(days=90)).isoformat()
        status, expiry = compute_cert_status([{"endDateTime": future}])
        assert status == "Valid"
        assert expiry != "---"

    def test_expiring_soon(self) -> None:
        soon = (datetime.now(tz=timezone.utc) + timedelta(days=15)).isoformat()
        status, _expiry = compute_cert_status([{"endDateTime": soon}])
        assert status == "Expiring soon"

    def test_expired(self) -> None:
        past = (datetime.now(tz=timezone.utc) - timedelta(days=10)).isoformat()
        status, _expiry = compute_cert_status([{"endDateTime": past}])
        assert status == "Expired"

    def test_picks_latest_expiry(self) -> None:
        old = (datetime.now(tz=timezone.utc) - timedelta(days=10)).isoformat()
        new = (datetime.now(tz=timezone.utc) + timedelta(days=90)).isoformat()
        status, _expiry = compute_cert_status([
            {"endDateTime": old},
            {"endDateTime": new},
        ])
        assert status == "Valid"


# ---------------------------------------------------------------------------
# fetch_all_service_principals
# ---------------------------------------------------------------------------


class TestFetchAllServicePrincipals:
    @responses.activate
    def test_fetches_with_pagination(self) -> None:
        page1_url_pattern = f"{GRAPH_BASE}/servicePrincipals"
        page2_url = f"{GRAPH_BASE}/servicePrincipals?skiptoken=page2"

        responses.add(
            responses.GET,
            page1_url_pattern,
            json={
                "value": [make_sp("sp-1", "App One")],
                "@odata.nextLink": page2_url,
            },
            status=200,
        )
        responses.add(
            responses.GET,
            page2_url,
            json={"value": [make_sp("sp-2", "App Two")]},
            status=200,
        )

        client = GraphClient(FAKE_TOKEN)
        apps = fetch_all_service_principals(client)
        assert len(apps) == 2
        assert apps[0]["displayName"] == "App One"
        assert apps[1]["displayName"] == "App Two"


# ---------------------------------------------------------------------------
# fetch_assignments_count
# ---------------------------------------------------------------------------


class TestFetchAssignmentsCount:
    @responses.activate
    def test_returns_count(self) -> None:
        url = f"{GRAPH_BASE}/servicePrincipals/sp-1/appRoleAssignedTo/$count"
        responses.add(responses.GET, url, body="5", status=200)
        client = GraphClient(FAKE_TOKEN)
        assert fetch_assignments_count(client, "sp-1") == 5

    @responses.activate
    def test_returns_zero_on_error(self) -> None:
        url = f"{GRAPH_BASE}/servicePrincipals/sp-1/appRoleAssignedTo/$count"
        responses.add(responses.GET, url, status=404)
        client = GraphClient(FAKE_TOKEN)
        assert fetch_assignments_count(client, "sp-1") == 0


# ---------------------------------------------------------------------------
# display_list_table
# ---------------------------------------------------------------------------


class TestDisplayListTable:
    def test_prints_table(self, capsys: pytest.CaptureFixture[str]) -> None:
        apps = [make_sp("sp-1", "App One"), make_sp("sp-2", "App Two")]
        display_list_table(apps)
        out = capsys.readouterr().out
        assert "App One" in out
        assert "App Two" in out
        assert "Total: 2" in out


# ---------------------------------------------------------------------------
# show_app_details
# ---------------------------------------------------------------------------


class TestShowAppDetails:
    @responses.activate
    def test_displays_properties(self, capsys: pytest.CaptureFixture[str]) -> None:
        sp = make_sp("sp-1", "Test App Detail")
        # Mock owners
        responses.add(
            responses.GET,
            f"{GRAPH_BASE}/servicePrincipals/sp-1/owners",
            json={"value": [{"displayName": "Owner1", "userPrincipalName": "o@test.com"}]},
            status=200,
        )
        # Mock appRoles
        responses.add(
            responses.GET,
            f"{GRAPH_BASE}/servicePrincipals/sp-1",
            json={"appRoles": []},
            status=200,
        )
        # Mock appRoleAssignments (granted API permissions)
        responses.add(
            responses.GET,
            f"{GRAPH_BASE}/servicePrincipals/sp-1/appRoleAssignments",
            json={"value": []},
            status=200,
        )
        # Mock assignments (users/groups)
        responses.add(
            responses.GET,
            f"{GRAPH_BASE}/servicePrincipals/sp-1/appRoleAssignedTo",
            json={"value": []},
            status=200,
        )
        # Mock SSO
        responses.add(
            responses.GET,
            f"{GRAPH_BASE}/servicePrincipals/sp-1",
            json={"preferredSingleSignOnMode": "saml"},
            status=200,
        )
        # Mock provisioning
        responses.add(
            responses.GET,
            f"{GRAPH_BASE}/servicePrincipals/sp-1/synchronization/jobs",
            json={"value": []},
            status=200,
        )

        client = GraphClient(FAKE_TOKEN)
        show_app_details(client, sp)
        out = capsys.readouterr().out
        assert "Test App Detail" in out
        assert "Owner1" in out
        assert "Roles and Administrators" in out
        assert "Granted API Permissions" in out

    @responses.activate
    def test_displays_granted_permissions(self, capsys: pytest.CaptureFixture[str]) -> None:
        sp = make_sp("sp-1", "Perm App")
        # Mock owners
        responses.add(
            responses.GET,
            f"{GRAPH_BASE}/servicePrincipals/sp-1/owners",
            json={"value": []},
            status=200,
        )
        # Mock appRoles
        responses.add(
            responses.GET,
            f"{GRAPH_BASE}/servicePrincipals/sp-1",
            json={"appRoles": []},
            status=200,
        )
        # Mock appRoleAssignments with data
        responses.add(
            responses.GET,
            f"{GRAPH_BASE}/servicePrincipals/sp-1/appRoleAssignments",
            json={"value": [
                {
                    "resourceDisplayName": "Microsoft Graph",
                    "appRoleId": "abcd1234-5678-9012-3456-789012345678",
                },
            ]},
            status=200,
        )
        # Mock assignments
        responses.add(
            responses.GET,
            f"{GRAPH_BASE}/servicePrincipals/sp-1/appRoleAssignedTo",
            json={"value": []},
            status=200,
        )
        # Mock SSO
        responses.add(
            responses.GET,
            f"{GRAPH_BASE}/servicePrincipals/sp-1",
            json={"preferredSingleSignOnMode": None},
            status=200,
        )
        # Mock provisioning
        responses.add(
            responses.GET,
            f"{GRAPH_BASE}/servicePrincipals/sp-1/synchronization/jobs",
            json={"value": []},
            status=200,
        )

        client = GraphClient(FAKE_TOKEN)
        show_app_details(client, sp)
        out = capsys.readouterr().out
        assert "Microsoft Graph" in out
        assert "abcd1234" in out


# ---------------------------------------------------------------------------
# delete_apps
# ---------------------------------------------------------------------------


class TestDeleteApps:
    @patch("src.tools.enterprise_apps.tool.get_client_credentials_token")
    def test_delete_confirmed(
        self,
        mock_token: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_token.return_value = FAKE_TOKEN
        apps = [make_sp("sp-1", "DeleteMe")]

        # User confirms deletion
        monkeypatch.setattr("builtins.input", lambda _: "y")

        with responses.RequestsMock() as rsps:
            rsps.add(responses.DELETE, f"{GRAPH_BASE}/servicePrincipals/sp-1", status=204)
            delete_apps(apps, make_env(), [1])

    @patch("src.tools.enterprise_apps.tool.get_client_credentials_token")
    def test_delete_skipped(
        self,
        mock_token: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        mock_token.return_value = FAKE_TOKEN
        apps = [make_sp("sp-1", "SkipMe")]

        # User declines deletion
        monkeypatch.setattr("builtins.input", lambda _: "n")
        delete_apps(apps, make_env(), [1])

        out = capsys.readouterr().out
        assert "Skipped" in out
