"""Extract all emails from a PST file and export them as readable JSON files.

Uses Outlook COM automation (pywin32) to open the PST, walk every folder,
and save each message as a JSON file with full metadata and body content.

Output structure:
    output_dir/
        _index.json          — master index of all extracted emails
        Inbox/
            0001_subject.json
            0002_subject.json
        Sent Items/
            0001_subject.json
        ...
"""

import json
import os
import re
import signal
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PST_PATH = (
    r"H:\Australis Dropbox\1. Company Administration"
    r"\Australis Navigator Pty Ltd\C9 Software Development"
    r"\Email History to 26 Feb 2026\Exchange.001.pst"
)
OUTPUT_DIR = Path(__file__).resolve().parent / "extracted_emails"
SAVE_ATTACHMENTS = True
MAX_FILENAME_LEN = 80

# Outlook item types we care about
OL_MAIL_ITEM = 43
OL_POST_ITEM = 45

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_interrupted = False


def _handle_sigint(sig: int, frame: object) -> None:
    global _interrupted
    print("\n[!] Ctrl+C detected — finishing current email then stopping…")
    _interrupted = True


signal.signal(signal.SIGINT, _handle_sigint)


def sanitize_filename(name: str) -> str:
    """Remove characters that are invalid in Windows filenames."""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    name = name.strip('. ')
    if not name:
        name = '_no_subject_'
    return name[:MAX_FILENAME_LEN]


def com_date_to_iso(com_date: object) -> str | None:
    """Convert a COM date (pywintypes.datetime) to an ISO-8601 string."""
    if com_date is None:
        return None
    try:
        # pywintypes.datetime has .isoformat() in most cases
        return com_date.isoformat()
    except AttributeError:
        pass
    try:
        return str(com_date)
    except Exception:
        return None


def safe_str(value: object) -> str:
    """Safely convert any COM property to a string."""
    if value is None:
        return ""
    try:
        return str(value)
    except Exception:
        return ""


def extract_recipients(mail_item: object) -> list[dict[str, str]]:
    """Extract recipient names and addresses from a mail item."""
    recipients: list[dict[str, str]] = []
    try:
        for i in range(1, mail_item.Recipients.Count + 1):
            recip = mail_item.Recipients.Item(i)
            recipients.append({
                "name": safe_str(recip.Name),
                "address": safe_str(recip.Address),
                "type": {1: "To", 2: "CC", 3: "BCC"}.get(recip.Type, "Unknown"),
            })
    except Exception:
        pass
    return recipients


def extract_attachments(
    mail_item: object, folder_path: Path, email_prefix: str
) -> list[dict[str, str]]:
    """Save attachments and return metadata about them."""
    attachments: list[dict[str, str]] = []
    if not SAVE_ATTACHMENTS:
        return attachments
    try:
        count = mail_item.Attachments.Count
        if count == 0:
            return attachments
        att_dir = folder_path / f"{email_prefix}_attachments"
        att_dir.mkdir(parents=True, exist_ok=True)
        for i in range(1, count + 1):
            att = mail_item.Attachments.Item(i)
            fname = sanitize_filename(safe_str(att.FileName)) or f"attachment_{i}"
            save_path = att_dir / fname
            try:
                att.SaveAsFile(str(save_path))
                attachments.append({
                    "filename": fname,
                    "path": str(save_path),
                    "size": att.Size if hasattr(att, 'Size') else 0,
                })
            except Exception as e:
                attachments.append({
                    "filename": fname,
                    "error": str(e),
                })
    except Exception:
        pass
    return attachments


def extract_email(mail_item: object) -> dict | None:
    """Extract all readable fields from a single mail item."""
    try:
        data: dict = {
            "subject": safe_str(mail_item.Subject),
            "sender_name": safe_str(mail_item.SenderName),
            "sender_email": "",
            "received_time": com_date_to_iso(
                getattr(mail_item, "ReceivedTime", None)
            ),
            "sent_on": com_date_to_iso(getattr(mail_item, "SentOn", None)),
            "recipients": extract_recipients(mail_item),
            "body": safe_str(mail_item.Body),
            "html_body": "",
            "categories": safe_str(getattr(mail_item, "Categories", "")),
            "importance": getattr(mail_item, "Importance", 1),
            "conversation_topic": safe_str(
                getattr(mail_item, "ConversationTopic", "")
            ),
            "attachments": [],
        }
        # Sender email — try multiple properties
        try:
            data["sender_email"] = safe_str(mail_item.SenderEmailAddress)
        except Exception:
            pass
        # HTML body can sometimes fail
        try:
            data["html_body"] = safe_str(mail_item.HTMLBody)
        except Exception:
            pass
        return data
    except Exception as e:
        return {"error": str(e)}


def process_folder(
    folder: object,
    parent_path: Path,
    index: list[dict],
    stats: dict,
) -> None:
    """Recursively process an Outlook folder and all sub-folders."""
    global _interrupted
    if _interrupted:
        return

    folder_name = sanitize_filename(safe_str(folder.Name))
    folder_path = parent_path / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)

    relative_folder = folder_path.relative_to(OUTPUT_DIR)
    print(f"  Processing: {relative_folder} ", end="", flush=True)

    # Process items in this folder
    try:
        items = folder.Items
        item_count = items.Count
        print(f"({item_count} items)")
    except Exception:
        print("(unable to read items)")
        item_count = 0

    email_num = 0
    for i in range(1, item_count + 1):
        if _interrupted:
            break
        try:
            item = items.Item(i)
            item_class = getattr(item, "Class", 0)
            if item_class not in (OL_MAIL_ITEM, OL_POST_ITEM):
                stats["skipped"] += 1
                continue

            email_num += 1
            prefix = f"{email_num:04d}"
            subject_slug = sanitize_filename(safe_str(item.Subject))
            filename = f"{prefix}_{subject_slug}.json"

            data = extract_email(item)
            if data is None:
                stats["errors"] += 1
                continue

            # Save attachments
            data["attachments"] = extract_attachments(item, folder_path, prefix)

            # Write JSON
            json_path = folder_path / filename
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

            # Add to master index
            index.append({
                "folder": str(relative_folder),
                "file": filename,
                "subject": data.get("subject", ""),
                "sender": data.get("sender_name", ""),
                "date": data.get("received_time") or data.get("sent_on", ""),
            })

            stats["extracted"] += 1
            if stats["extracted"] % 100 == 0:
                print(f"    … {stats['extracted']} emails extracted so far")

        except Exception as e:
            stats["errors"] += 1
            if stats["errors"] <= 20:
                print(f"    [error] Item {i}: {e}")

    # Recurse into sub-folders
    try:
        for j in range(1, folder.Folders.Count + 1):
            if _interrupted:
                break
            process_folder(folder.Folders.Item(j), folder_path, index, stats)
    except Exception:
        pass


def main() -> None:
    global _interrupted

    # Validate PST exists
    if not os.path.isfile(PST_PATH):
        print(f"[ERROR] PST file not found: {PST_PATH}")
        print("Please check the path and try again.")
        input("Press Enter to exit…")
        sys.exit(1)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("PST Email Extractor")
    print("=" * 70)
    print(f"  PST file : {PST_PATH}")
    print(f"  Output   : {OUTPUT_DIR}")
    print(f"  Attach.  : {'Yes' if SAVE_ATTACHMENTS else 'No'}")
    print()

    # Connect to Outlook via COM
    print("[1/4] Connecting to Outlook…")
    try:
        import win32com.client
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
    except Exception as e:
        print(f"[ERROR] Could not connect to Outlook: {e}")
        print("Make sure Outlook is installed and not running as admin.")
        input("Press Enter to exit…")
        sys.exit(1)

    # Add the PST store
    print("[2/4] Loading PST file (this may take a moment for large files)…")
    try:
        namespace.AddStore(PST_PATH)
        time.sleep(2)  # Give Outlook time to mount the store
    except Exception as e:
        print(f"[ERROR] Could not load PST: {e}")
        input("Press Enter to exit…")
        sys.exit(1)

    # Find the newly added PST store
    # It will be the last store/folder added, or we match by name
    pst_root = None
    for i in range(namespace.Folders.Count, 0, -1):
        folder = namespace.Folders.Item(i)
        folder_name = safe_str(folder.Name)
        # The PST store name usually matches the filename or "Outlook Data File"
        if "exchange" in folder_name.lower() or "personal" in folder_name.lower():
            pst_root = folder
            print(f"  Found PST store: {folder_name}")
            break

    # If not found by name, take the last folder (most recently added)
    if pst_root is None:
        pst_root = namespace.Folders.Item(namespace.Folders.Count)
        print(f"  Using store: {safe_str(pst_root.Name)}")

    # Walk all folders and extract emails
    print("[3/4] Extracting emails…")
    print()

    index: list[dict] = []
    stats = {"extracted": 0, "skipped": 0, "errors": 0}

    try:
        for i in range(1, pst_root.Folders.Count + 1):
            if _interrupted:
                break
            process_folder(pst_root.Folders.Item(i), OUTPUT_DIR, index, stats)
    except Exception as e:
        print(f"\n[ERROR] Extraction failed: {e}")

    # Remove the PST store to clean up
    print()
    print("[4/4] Cleaning up — removing PST from Outlook…")
    try:
        namespace.RemoveStore(pst_root)
    except Exception:
        print("  (Could not auto-remove PST — you may need to remove it")
        print("   manually in Outlook: right-click the store → Close)")

    # Write master index
    index_path = OUTPUT_DIR / "_index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False, default=str)

    # Summary
    print()
    print("=" * 70)
    print("Extraction Complete")
    print("=" * 70)
    print(f"  Emails extracted : {stats['extracted']}")
    print(f"  Non-email items  : {stats['skipped']}")
    print(f"  Errors           : {stats['errors']}")
    print(f"  Master index     : {index_path}")
    print(f"  Output directory : {OUTPUT_DIR}")
    if _interrupted:
        print("  ** Extraction was interrupted — results are partial **")
    print()


if __name__ == "__main__":
    main()
