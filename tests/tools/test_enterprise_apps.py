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
    fetch_all_assignments,
    fetch_all_service_principals,
    fetch_assignments_count,
    show_app_details,
    sort_apps,
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
        url = f"{GRAPH_BASE}/servicePrincipals/sp-1/appRoleAssignedTo"
        responses.add(
            responses.GET, url,
            json={"@odata.count": 5, "value": []},
            status=200,
        )
        client = GraphClient(FAKE_TOKEN)
        assert fetch_assignments_count(client, "sp-1") == 5

    @responses.activate
    def test_returns_zero_when_no_count(self) -> None:
        url = f"{GRAPH_BASE}/servicePrincipals/sp-1/appRoleAssignedTo"
        responses.add(
            responses.GET, url,
            json={"value": []},
            status=200,
        )
        client = GraphClient(FAKE_TOKEN)
        assert fetch_assignments_count(client, "sp-1") == 0

    @responses.activate
    def test_returns_zero_on_error(self) -> None:
        url = f"{GRAPH_BASE}/servicePrincipals/sp-1/appRoleAssignedTo"
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


# ---------------------------------------------------------------------------
# sort_apps
# ---------------------------------------------------------------------------


class TestSortApps:
    def test_sort_by_name(self) -> None:
        apps = [make_sp("sp-2", "Zebra"), make_sp("sp-1", "Alpha"), make_sp("sp-3", "middle")]
        sort_apps(apps, "name")
        assert [a["displayName"] for a in apps] == ["Alpha", "middle", "Zebra"]

    def test_sort_by_created(self) -> None:
        apps = [
            {**make_sp("sp-1"), "createdDateTime": "2025-06-01T00:00:00Z"},
            {**make_sp("sp-2"), "createdDateTime": "2025-01-01T00:00:00Z"},
            {**make_sp("sp-3"), "createdDateTime": ""},
        ]
        sort_apps(apps, "created")
        assert apps[0]["id"] == "sp-2"  # oldest first
        assert apps[2]["id"] == "sp-3"  # missing last

    def test_sort_by_cert_expiry(self) -> None:
        future_near = (datetime.now(tz=timezone.utc) + timedelta(days=10)).isoformat()
        future_far = (datetime.now(tz=timezone.utc) + timedelta(days=90)).isoformat()
        apps = [
            make_sp("sp-1", "NoCert"),
            make_sp("sp-2", "Far", key_credentials=[{"endDateTime": future_far}]),
            make_sp("sp-3", "Near", key_credentials=[{"endDateTime": future_near}]),
        ]
        sort_apps(apps, "cert_expiry")
        assert apps[0]["id"] == "sp-3"  # soonest first
        assert apps[1]["id"] == "sp-2"  # further later
        assert apps[2]["id"] == "sp-1"  # no cert last

    def test_sort_by_assignments(self) -> None:
        apps = [
            {**make_sp("sp-1"), "_assignments_count": 2},
            {**make_sp("sp-2"), "_assignments_count": 10},
            {**make_sp("sp-3"), "_assignments_count": "---"},
        ]
        sort_apps(apps, "assignments")
        assert apps[0]["id"] == "sp-2"  # most first
        assert apps[1]["id"] == "sp-1"
        assert apps[2]["id"] == "sp-3"  # unfetched last


# ---------------------------------------------------------------------------
# fetch_all_assignments
# ---------------------------------------------------------------------------


class TestFetchAllAssignments:
    @responses.activate
    def test_fetches_only_missing(self) -> None:
        apps = [
            {**make_sp("sp-1"), "_assignments_count": 5},
            {**make_sp("sp-2"), "_assignments_count": "---"},
            {**make_sp("sp-3")},  # no key at all → defaults to "---"
        ]
        # Mock for sp-2 and sp-3
        for sp_id, count in [("sp-2", 3), ("sp-3", 7)]:
            responses.add(
                responses.GET,
                f"{GRAPH_BASE}/servicePrincipals/{sp_id}/appRoleAssignedTo",
                json={"@odata.count": count, "value": []},
                status=200,
            )
        client = GraphClient(FAKE_TOKEN)
        fetch_all_assignments(client, apps)
        assert apps[0]["_assignments_count"] == 5  # unchanged
        assert apps[1]["_assignments_count"] == 3
        assert apps[2]["_assignments_count"] == 7

    def test_noop_when_all_fetched(self) -> None:
        apps = [
            {**make_sp("sp-1"), "_assignments_count": 5},
            {**make_sp("sp-2"), "_assignments_count": 0},
        ]
        client = GraphClient(FAKE_TOKEN)
        # Should not make any HTTP calls — no mocks needed
        fetch_all_assignments(client, apps)
        assert apps[0]["_assignments_count"] == 5
        assert apps[1]["_assignments_count"] == 0


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
