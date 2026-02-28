"""Tests for src.core.graph_client."""

from __future__ import annotations

import pytest
import responses

from src.core.config import GRAPH_BASE
from src.core.graph_client import GraphClient, GraphPermissionError, TenantMismatchError
from tests.conftest import CHAT_ID, FAKE_TOKEN


class TestGraphClientGet:
    @responses.activate
    def test_success(self) -> None:
        url = f"{GRAPH_BASE}/me"
        responses.add(responses.GET, url, json={"displayName": "Test"}, status=200)
        client = GraphClient(FAKE_TOKEN)
        resp = client.get(url)
        assert resp.json()["displayName"] == "Test"

    @responses.activate
    def test_retry_on_429(self) -> None:
        url = f"{GRAPH_BASE}/me"
        responses.add(responses.GET, url, status=429, headers={"Retry-After": "0"})
        responses.add(responses.GET, url, json={"ok": True}, status=200)
        client = GraphClient(FAKE_TOKEN)
        resp = client.get(url)
        assert resp.json()["ok"] is True

    @responses.activate
    def test_retry_on_500(self) -> None:
        url = f"{GRAPH_BASE}/me"
        responses.add(responses.GET, url, status=500, headers={"Retry-After": "0"})
        responses.add(responses.GET, url, json={"ok": True}, status=200)
        client = GraphClient(FAKE_TOKEN)
        resp = client.get(url)
        assert resp.json()["ok"] is True


class TestGraphClientGetPaged:
    @responses.activate
    def test_single_page(self) -> None:
        url = f"{GRAPH_BASE}/items"
        responses.add(responses.GET, url, json={"value": [{"id": 1}]}, status=200)
        client = GraphClient(FAKE_TOKEN)
        items = client.get_paged(url)
        assert len(items) == 1

    @responses.activate
    def test_multiple_pages(self) -> None:
        page1 = f"{GRAPH_BASE}/items"
        page2 = f"{GRAPH_BASE}/items?skip=1"
        responses.add(
            responses.GET, page1,
            json={"value": [{"id": 1}], "@odata.nextLink": page2}, status=200,
        )
        responses.add(
            responses.GET, page2,
            json={"value": [{"id": 2}]}, status=200,
        )
        client = GraphClient(FAKE_TOKEN)
        items = client.get_paged(page1)
        assert len(items) == 2


class TestTenantMismatchDetection:
    @responses.activate
    def test_403_tenant_mismatch_in_message(self) -> None:
        url = f"{GRAPH_BASE}/chats/{CHAT_ID}/messages?$top=50"
        responses.add(
            responses.GET, url,
            json={
                "error": {
                    "code": "Forbidden",
                    "message": "Tenant Id mismatch. The chat is owned by a different tenant.",
                }
            },
            status=403,
        )
        client = GraphClient(FAKE_TOKEN)
        with pytest.raises(TenantMismatchError):
            client.get(url)

    @responses.activate
    def test_403_tenant_mismatch_in_inner_error(self) -> None:
        url = f"{GRAPH_BASE}/chats/{CHAT_ID}/messages?$top=50"
        responses.add(
            responses.GET, url,
            json={
                "error": {
                    "code": "Forbidden",
                    "message": "InsufficientPrivileges",
                    "innerError": {
                        "code": "1",
                        "message": "AclCheckFailed. Tenant Id mismatch.",
                    },
                }
            },
            status=403,
        )
        client = GraphClient(FAKE_TOKEN)
        with pytest.raises(TenantMismatchError):
            client.get(url)

    @responses.activate
    def test_403_other_error_raises_permission_error(self) -> None:
        url = f"{GRAPH_BASE}/chats/{CHAT_ID}/messages?$top=50"
        responses.add(
            responses.GET, url,
            json={
                "error": {
                    "code": "Authorization_RequestDenied",
                    "message": "Insufficient privileges to complete the operation.",
                }
            },
            status=403,
        )
        client = GraphClient(FAKE_TOKEN)
        with pytest.raises(GraphPermissionError, match="Insufficient privileges"):
            client.get(url)


class TestGraphClientPost:
    @responses.activate
    def test_post_success(self) -> None:
        url = f"{GRAPH_BASE}/users"
        responses.add(responses.POST, url, json={"id": "new-user"}, status=201)
        client = GraphClient(FAKE_TOKEN)
        resp = client.post(url, json_body={"displayName": "Test"})
        assert resp.status_code == 201
        assert resp.json()["id"] == "new-user"

    @responses.activate
    def test_post_sends_json_body(self) -> None:
        url = f"{GRAPH_BASE}/groups"
        responses.add(responses.POST, url, json={"id": "g1"}, status=201)
        client = GraphClient(FAKE_TOKEN)
        client.post(url, json_body={"displayName": "Group"})
        assert responses.calls[0].request.body == b'{"displayName": "Group"}'


class TestGraphClientPatch:
    @responses.activate
    def test_patch_success(self) -> None:
        url = f"{GRAPH_BASE}/users/user-1"
        responses.add(responses.PATCH, url, status=204)
        client = GraphClient(FAKE_TOKEN)
        resp = client.patch(url, json_body={"accountEnabled": False})
        assert resp.status_code == 204

    @responses.activate
    def test_patch_sends_json_body(self) -> None:
        url = f"{GRAPH_BASE}/users/user-1"
        responses.add(responses.PATCH, url, status=204)
        client = GraphClient(FAKE_TOKEN)
        client.patch(url, json_body={"displayName": "Updated"})
        assert responses.calls[0].request.body == b'{"displayName": "Updated"}'


class TestGraphClientDelete:
    @responses.activate
    def test_delete_success(self) -> None:
        url = f"{GRAPH_BASE}/servicePrincipals/sp-id"
        responses.add(responses.DELETE, url, status=204)
        client = GraphClient(FAKE_TOKEN)
        resp = client.delete(url)
        assert resp.status_code == 204
