"""Teams Chat Export — export messages and media from a Microsoft Teams chat.

Usage (standalone):
    python -m src  →  select "Teams Chat Export" from menu

Authentication modes:
    Client credentials (default) — uses AZURE_CLIENT_SECRET for app-level access.
    Interactive browser (--delegated) — user signs in via browser for delegated access.
"""

from __future__ import annotations

import csv
import re
import mimetypes
import pathlib
from datetime import datetime, timezone

import requests

from src.core.auth import get_client_credentials_token, get_delegated_token
from src.core.config import DOWNLOAD_TIMEOUT, GRAPH_BASE, load_environment
from src.core.graph_client import GraphClient, TenantMismatchError
from src.core.utils import save_json, write_with_lock_check
from src.tools._base import ToolDefinition


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_CHAT_ID = "19:100f413daad743e583920058430ec675@thread.v2"
DELEGATED_SCOPES = ["Chat.Read", "Chat.ReadBasic", "User.Read"]

_HOSTED_CONTENT_RE = re.compile(
    r'<img\s[^>]*src="[^"]*hostedContents/([^/"]+)/\$value"',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------


def fetch_all_messages(chat_id: str, client: GraphClient) -> list[dict]:
    """Fetch every message in a chat, following @odata.nextLink pagination."""
    url = f"{GRAPH_BASE}/chats/{chat_id}/messages?$top=50"
    return client.get_paged(url, page_label="messages")


# ---------------------------------------------------------------------------
# Media helpers
# ---------------------------------------------------------------------------


def parse_hosted_content_ids(html: str) -> list[str]:
    """Return hosted-content IDs found in message HTML body."""
    return _HOSTED_CONTENT_RE.findall(html)


def _guess_extension(content_type: str | None) -> str:
    if not content_type:
        return ".bin"
    ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
    return ext or ".bin"


def download_hosted_content(
    chat_id: str,
    message_id: str,
    hosted_id: str,
    client: GraphClient,
    media_dir: pathlib.Path,
) -> dict:
    """Download a single hosted-content blob and return metadata."""
    url = (
        f"{GRAPH_BASE}/chats/{chat_id}/messages/{message_id}"
        f"/hostedContents/{hosted_id}/$value"
    )
    try:
        resp = client.get(url, timeout=DOWNLOAD_TIMEOUT, stream=True)
    except Exception as exc:
        print(f"    WARN: Failed to download hosted content {hosted_id}: {exc}")
        return {"id": hosted_id, "download_failed": True, "error": str(exc)}

    content_type = resp.headers.get("Content-Type")
    ext = _guess_extension(content_type)
    filename = f"hosted_{hosted_id}{ext}"
    filepath = media_dir / filename

    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return {"id": hosted_id, "contentType": content_type, "local_path": f"media/{filename}"}


def download_file_attachment(
    content_url: str,
    name: str,
    client: GraphClient,
    media_dir: pathlib.Path,
) -> str | None:
    """Download a file attachment via its contentUrl. Returns local path or None."""
    safe_name = re.sub(r'[<>:"/\\|?*]', "_", name)
    filename = f"attach_{safe_name}"
    filepath = media_dir / filename

    try:
        resp = client.get(content_url, timeout=DOWNLOAD_TIMEOUT, stream=True)
    except Exception as exc:
        print(f"    WARN: Failed to download attachment {name}: {exc}")
        return None

    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return f"media/{filename}"


def process_message_media(
    message: dict,
    chat_id: str,
    client: GraphClient,
    media_dir: pathlib.Path,
) -> dict:
    """Download hosted images and attachments, update message dict in place."""
    msg_id = message.get("id", "unknown")
    body = message.get("body", {})
    html = body.get("content", "") or ""

    if html:
        body["content_original"] = html

    # --- Hosted content images ---
    hosted_ids = parse_hosted_content_ids(html)
    hosted_results: list[dict] = []
    for hid in hosted_ids:
        info = download_hosted_content(chat_id, msg_id, hid, client, media_dir)
        hosted_results.append(info)
        if not info.get("download_failed") and info.get("local_path"):
            html = re.sub(
                rf'(<img\s[^>]*src=")[^"]*hostedContents/{re.escape(hid)}/\$value"',
                rf'\1{info["local_path"]}"',
                html,
                flags=re.IGNORECASE,
            )

    if hosted_results:
        message["hostedContents"] = hosted_results
        body["content"] = html

    # --- File attachments ---
    attachments = message.get("attachments", []) or []
    for att in attachments:
        content_url = att.get("contentUrl")
        att_name = att.get("name", att.get("id", "unknown"))
        if content_url:
            local = download_file_attachment(content_url, att_name, client, media_dir)
            if local:
                att["local_path"] = local
            else:
                att["download_failed"] = True

    return message


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def save_csv(messages: list[dict], path: pathlib.Path) -> None:
    """Write a flattened CSV summary of messages (UTF-8 with BOM for Excel)."""
    fieldnames = [
        "id", "createdDateTime", "from_displayName", "contentType",
        "message_preview", "attachments_count", "media_count", "webUrl",
    ]

    def _write(p: pathlib.Path) -> None:
        with open(p, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for msg in messages:
                from_user = (msg.get("from") or {}).get("user") or {}
                body = msg.get("body") or {}
                content = body.get("content", "") or ""
                preview = re.sub(r"<[^>]+>", "", content)[:200]
                hosted = msg.get("hostedContents", [])
                writer.writerow({
                    "id": msg.get("id", ""),
                    "createdDateTime": msg.get("createdDateTime", ""),
                    "from_displayName": from_user.get("displayName", ""),
                    "contentType": body.get("contentType", ""),
                    "message_preview": preview,
                    "attachments_count": len(msg.get("attachments") or []),
                    "media_count": len(hosted),
                    "webUrl": msg.get("webUrl", ""),
                })

    write_with_lock_check(path, _write)
    print(f"  Saved {path}")


def save_markdown(
    messages: list[dict],
    path: pathlib.Path,
    export_dir: pathlib.Path,
) -> None:
    """Write a Markdown conversation log with absolute image paths."""
    abs_export = export_dir.resolve()

    def _write(p: pathlib.Path) -> None:
        lines: list[str] = [
            "# Teams Chat Export\n",
            f"Exported: {datetime.now(tz=timezone.utc).isoformat()}\n",
            f"Messages: {len(messages)}\n",
            "---\n",
        ]
        for msg in messages:
            ts = msg.get("createdDateTime", "")
            from_user = (msg.get("from") or {}).get("user") or {}
            display_name = from_user.get("displayName", "System")
            body = msg.get("body") or {}
            content = body.get("content", "") or ""

            text = re.sub(r"<br\s*/?>", "\n", content, flags=re.IGNORECASE)
            text = re.sub(r"<[^>]+>", "", text).strip()

            lines.append(f"## [{ts}] {display_name}\n")
            if text:
                lines.append(f"{text}\n")

            for hc in msg.get("hostedContents") or []:
                local = hc.get("local_path")
                if local and not hc.get("download_failed"):
                    abs_path = abs_export / local
                    lines.append(f"\n![image]({abs_path})\n")
                    lines.append(f"<!-- Read {abs_path} -->\n")

            for att in msg.get("attachments") or []:
                local = att.get("local_path")
                att_name = att.get("name", "attachment")
                if local and not att.get("download_failed"):
                    abs_path = abs_export / local
                    lines.append(f"\nAttachment: **{att_name}** --- `{abs_path}`\n")

            lines.append("")

        p.write_text("\n".join(lines), encoding="utf-8")

    write_with_lock_check(path, _write)
    print(f"  Saved {path}")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------


def run() -> None:
    """Interactive entry point for the Teams Chat Export tool."""
    print("Teams Chat Export")

    try:
        chat_id = input(f"  Enter chat ID [{DEFAULT_CHAT_ID}]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        return
    if not chat_id:
        chat_id = DEFAULT_CHAT_ID

    print(f"  Chat ID: {chat_id}")

    try:
        use_delegated = input("  Use delegated (browser) auth? [y/N]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        return

    # --- Setup export directory ---
    sanitized = re.sub(r'[<>:"/\\|?*@]', "_", chat_id)[:80]
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    export_dir = pathlib.Path("exports") / f"{sanitized}_{timestamp}"
    media_dir = export_dir / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    print(f"  Export directory: {export_dir}")

    # --- Authenticate ---
    print("\nLoading environment ...")
    env = load_environment()

    if use_delegated == "y":
        print("Using delegated auth (browser sign-in) ...")
        token = get_delegated_token(env, DELEGATED_SCOPES)
    elif "AZURE_CLIENT_SECRET" not in env:
        print("No AZURE_CLIENT_SECRET found — using delegated auth ...")
        token = get_delegated_token(env, DELEGATED_SCOPES)
    else:
        print("Acquiring access token (client credentials) ...")
        token = get_client_credentials_token(env)
    print("Authenticated successfully.\n")

    client = GraphClient(token)

    # --- Fetch messages ---
    errors: list[dict] = []
    messages: list[dict] = []
    media_downloaded = 0

    try:
        print("Fetching messages ...")
        try:
            messages = fetch_all_messages(chat_id, client)
        except TenantMismatchError:
            print(
                "\n  Cross-tenant chat detected — switching to browser sign-in ...\n"
            )
            token = get_delegated_token(env, DELEGATED_SCOPES)
            client = GraphClient(token)
            try:
                messages = fetch_all_messages(chat_id, client)
            except requests.exceptions.HTTPError as exc:
                resp = exc.response
                detail = ""
                if resp is not None:
                    try:
                        detail = resp.json().get("error", {}).get("message", "")
                    except Exception:
                        detail = resp.text[:300]
                print(f"\n  ERROR: Delegated auth also failed: {detail or exc}")
                return

        # --- Download media ---
        print("\nProcessing media ...")
        for i, msg in enumerate(messages, 1):
            body = msg.get("body", {})
            html = body.get("content", "") or ""
            attachments = msg.get("attachments") or []
            has_media = parse_hosted_content_ids(html) or any(
                a.get("contentUrl") for a in attachments
            )
            if not has_media:
                continue

            msg_id = msg.get("id", "unknown")
            print(f"  [{i}/{len(messages)}] Message {msg_id[:20]}... — downloading media")
            try:
                process_message_media(msg, chat_id, client, media_dir)
                for hc in msg.get("hostedContents", []):
                    if not hc.get("download_failed"):
                        media_downloaded += 1
                for att in msg.get("attachments", []):
                    if att.get("local_path") and not att.get("download_failed"):
                        media_downloaded += 1
            except Exception as exc:
                errors.append({
                    "message_id": msg_id,
                    "error": str(exc),
                    "operation": "process_message_media",
                })
                print(f"    ERROR: {exc}")

    except KeyboardInterrupt:
        print("\n\nInterrupted! Saving what we have so far ...")

    # --- Save outputs ---
    print("\nSaving outputs ...")
    output = {
        "export_metadata": {
            "chat_id": chat_id,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "message_count": len(messages),
            "media_downloaded": media_downloaded,
        },
        "messages": messages,
    }
    save_json(output, export_dir / "messages.json")
    save_markdown(messages, export_dir / "messages.md", export_dir)
    save_csv(messages, export_dir / "messages.csv")

    metadata = {
        "chat_id": chat_id,
        "export_timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "message_count": len(messages),
        "media_downloaded": media_downloaded,
        "errors": errors,
    }
    save_json(metadata, export_dir / "export_metadata.json")

    # --- Summary ---
    print("\nExport complete!")
    print(f"  Messages: {len(messages)}")
    print(f"  Media downloaded: {media_downloaded}")
    if errors:
        print(f"  Errors: {len(errors)}")
    print(f"  Output: {export_dir}")


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------

TOOL = ToolDefinition(
    name="Teams Chat Export",
    description="Export messages and media from a Microsoft Teams chat.",
    permissions_application=["Chat.Read.All"],
    permissions_delegated=["Chat.Read", "Chat.ReadBasic", "User.Read"],
    run=run,
)
