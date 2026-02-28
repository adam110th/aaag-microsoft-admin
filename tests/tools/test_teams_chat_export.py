"""Tests for src.tools.teams_chat_export."""

from __future__ import annotations

import pathlib

import responses

from src.core.config import GRAPH_BASE
from src.core.graph_client import GraphClient
from src.tools.teams_chat_export.tool import (
    download_file_attachment,
    download_hosted_content,
    fetch_all_messages,
    parse_hosted_content_ids,
    process_message_media,
    save_csv,
    save_markdown,
)
from tests.conftest import CHAT_ID, FAKE_TOKEN


def make_message(
    msg_id: str = "msg1",
    body_html: str = "<p>Hello</p>",
    attachments: list | None = None,
    display_name: str = "Test User",
) -> dict:
    """Factory for message dicts matching Graph API shape."""
    return {
        "id": msg_id,
        "createdDateTime": "2025-01-15T10:00:00Z",
        "from": {"user": {"displayName": display_name, "id": "user-id-1"}},
        "body": {"contentType": "html", "content": body_html},
        "attachments": attachments or [],
        "mentions": [],
        "reactions": [],
    }


# ---------------------------------------------------------------------------
# parse_hosted_content_ids
# ---------------------------------------------------------------------------


class TestParseHostedContentIds:
    def test_single_match(self) -> None:
        html = '<img src="../hostedContents/abc123/$value" alt="image">'
        assert parse_hosted_content_ids(html) == ["abc123"]

    def test_multiple_matches(self) -> None:
        html = (
            '<img src="../hostedContents/id1/$value">'
            '<img src="../hostedContents/id2/$value">'
        )
        assert parse_hosted_content_ids(html) == ["id1", "id2"]

    def test_no_matches(self) -> None:
        assert parse_hosted_content_ids("<p>No images here</p>") == []

    def test_empty_string(self) -> None:
        assert parse_hosted_content_ids("") == []

    def test_case_insensitive(self) -> None:
        html = '<IMG SRC="../hostedContents/ABC/$value">'
        assert parse_hosted_content_ids(html) == ["ABC"]


# ---------------------------------------------------------------------------
# fetch_all_messages
# ---------------------------------------------------------------------------


class TestFetchAllMessages:
    @responses.activate
    def test_single_page(self) -> None:
        url = f"{GRAPH_BASE}/chats/{CHAT_ID}/messages?$top=50"
        responses.add(
            responses.GET, url,
            json={"value": [make_message()], "@odata.count": 1}, status=200,
        )
        client = GraphClient(FAKE_TOKEN)
        msgs = fetch_all_messages(CHAT_ID, client)
        assert len(msgs) == 1
        assert msgs[0]["id"] == "msg1"

    @responses.activate
    def test_pagination(self) -> None:
        page1_url = f"{GRAPH_BASE}/chats/{CHAT_ID}/messages?$top=50"
        page2_url = f"{GRAPH_BASE}/chats/{CHAT_ID}/messages?$skiptoken=page2"
        responses.add(
            responses.GET, page1_url,
            json={"value": [make_message("m1")], "@odata.nextLink": page2_url},
            status=200,
        )
        responses.add(
            responses.GET, page2_url,
            json={"value": [make_message("m2")]}, status=200,
        )
        client = GraphClient(FAKE_TOKEN)
        msgs = fetch_all_messages(CHAT_ID, client)
        assert len(msgs) == 2
        assert [m["id"] for m in msgs] == ["m1", "m2"]

    @responses.activate
    def test_empty_chat(self) -> None:
        url = f"{GRAPH_BASE}/chats/{CHAT_ID}/messages?$top=50"
        responses.add(responses.GET, url, json={"value": []}, status=200)
        client = GraphClient(FAKE_TOKEN)
        assert fetch_all_messages(CHAT_ID, client) == []


# ---------------------------------------------------------------------------
# download_hosted_content
# ---------------------------------------------------------------------------


class TestDownloadHostedContent:
    @responses.activate
    def test_successful_download(self, media_dir: pathlib.Path) -> None:
        hosted_id = "hc1"
        url = (
            f"{GRAPH_BASE}/chats/{CHAT_ID}/messages/msg1"
            f"/hostedContents/{hosted_id}/$value"
        )
        responses.add(
            responses.GET, url,
            body=b"\x89PNG\r\n\x1a\n",
            headers={"Content-Type": "image/png"}, status=200,
        )
        client = GraphClient(FAKE_TOKEN)
        result = download_hosted_content(CHAT_ID, "msg1", hosted_id, client, media_dir)
        assert result["id"] == hosted_id
        assert result["local_path"] == "media/hosted_hc1.png"
        assert (media_dir / "hosted_hc1.png").exists()

    @responses.activate
    def test_download_failure(self, media_dir: pathlib.Path) -> None:
        hosted_id = "hc_bad"
        url = (
            f"{GRAPH_BASE}/chats/{CHAT_ID}/messages/msg1"
            f"/hostedContents/{hosted_id}/$value"
        )
        responses.add(responses.GET, url, status=404)
        client = GraphClient(FAKE_TOKEN)
        result = download_hosted_content(CHAT_ID, "msg1", hosted_id, client, media_dir)
        assert result["download_failed"] is True


# ---------------------------------------------------------------------------
# download_file_attachment
# ---------------------------------------------------------------------------


class TestDownloadFileAttachment:
    @responses.activate
    def test_successful_download(self, media_dir: pathlib.Path) -> None:
        url = "https://example.com/files/report.pdf"
        responses.add(responses.GET, url, body=b"%PDF-1.4", status=200)
        client = GraphClient(FAKE_TOKEN)
        result = download_file_attachment(url, "report.pdf", client, media_dir)
        assert result == "media/attach_report.pdf"
        assert (media_dir / "attach_report.pdf").exists()

    @responses.activate
    def test_download_failure(self, media_dir: pathlib.Path) -> None:
        url = "https://example.com/files/missing.pdf"
        responses.add(responses.GET, url, status=500)
        client = GraphClient(FAKE_TOKEN)
        result = download_file_attachment(url, "missing.pdf", client, media_dir)
        assert result is None

    @responses.activate
    def test_sanitizes_filename(self, media_dir: pathlib.Path) -> None:
        url = "https://example.com/files/weird"
        responses.add(responses.GET, url, body=b"data", status=200)
        client = GraphClient(FAKE_TOKEN)
        result = download_file_attachment(url, 'file:with"bad<chars>', client, media_dir)
        assert result is not None
        assert ":" not in result.replace("media/", "")


# ---------------------------------------------------------------------------
# process_message_media
# ---------------------------------------------------------------------------


class TestProcessMessageMedia:
    @responses.activate
    def test_replaces_hosted_content_src(self, media_dir: pathlib.Path) -> None:
        html = '<div><img src="../hostedContents/img1/$value" alt="pic"></div>'
        msg = make_message(body_html=html)
        url = (
            f"{GRAPH_BASE}/chats/{CHAT_ID}/messages/msg1"
            f"/hostedContents/img1/$value"
        )
        responses.add(
            responses.GET, url,
            body=b"\x89PNG",
            headers={"Content-Type": "image/png"}, status=200,
        )
        client = GraphClient(FAKE_TOKEN)
        process_message_media(msg, CHAT_ID, client, media_dir)
        assert "content_original" in msg["body"]
        assert "media/hosted_img1.png" in msg["body"]["content"]

    @responses.activate
    def test_no_media_noop(self, media_dir: pathlib.Path) -> None:
        msg = make_message(body_html="<p>Plain text</p>")
        client = GraphClient(FAKE_TOKEN)
        process_message_media(msg, CHAT_ID, client, media_dir)
        assert "hostedContents" not in msg


# ---------------------------------------------------------------------------
# save_csv / save_markdown
# ---------------------------------------------------------------------------


class TestSaveMarkdown:
    def test_writes_readable_conversation(self, tmp_path: pathlib.Path) -> None:
        msgs = [
            make_message(body_html="<p>Hello world</p>", display_name="Alice"),
            make_message(msg_id="m2", body_html="<p>Hi Alice!</p>", display_name="Bob"),
        ]
        path = tmp_path / "messages.md"
        save_markdown(msgs, path, tmp_path)
        text = path.read_text(encoding="utf-8")
        assert "# Teams Chat Export" in text
        assert "Alice" in text
        assert "Bob" in text
        assert "Hello world" in text

    def test_includes_image_paths(self, tmp_path: pathlib.Path) -> None:
        msg = make_message(body_html="<p>See image</p>")
        msg["hostedContents"] = [
            {"id": "img1", "contentType": "image/png", "local_path": "media/hosted_img1.png"}
        ]
        path = tmp_path / "messages.md"
        save_markdown([msg], path, tmp_path)
        text = path.read_text(encoding="utf-8")
        assert "hosted_img1.png" in text

    def test_includes_attachment_paths(self, tmp_path: pathlib.Path) -> None:
        msg = make_message()
        msg["attachments"] = [
            {"name": "report.pdf", "local_path": "media/attach_report.pdf"}
        ]
        path = tmp_path / "messages.md"
        save_markdown([msg], path, tmp_path)
        text = path.read_text(encoding="utf-8")
        assert "report.pdf" in text


class TestSaveCsv:
    def test_writes_csv_with_bom(self, tmp_path: pathlib.Path) -> None:
        msgs = [make_message()]
        path = tmp_path / "out.csv"
        save_csv(msgs, path)
        raw = path.read_bytes()
        assert raw[:3] == b"\xef\xbb\xbf"  # UTF-8 BOM
        text = raw.decode("utf-8-sig")
        assert "Test User" in text
        assert "id,createdDateTime" in text
