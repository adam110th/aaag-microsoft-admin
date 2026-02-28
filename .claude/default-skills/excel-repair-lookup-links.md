## MANDATORY — Excel External Link Repair

**This skill is NON-NEGOTIABLE.** Every time Claude Code creates or updates a Python script that saves an Excel workbook (.xlsx file) using openpyxl — or any library that uses openpyxl under the hood (including pandas with `engine="openpyxl"`) — the repair steps below MUST be included. No exceptions. Do not skip any step. Do not assume the file will be clean without repair.

### Trigger Conditions — Check Every Time

This skill MUST fire when ANY of the following are true:

- A script imports `openpyxl`
- A script calls `openpyxl.Workbook()`, `openpyxl.load_workbook()`, or `wb.save()`
- A script calls `pandas.DataFrame.to_excel()` or `pandas.ExcelWriter()` (these use openpyxl by default)
- A script writes, modifies, or saves any `.xlsx` file
- An existing script that saves `.xlsx` files is being edited for any reason

If any of these conditions are met, verify that ALL of the following repair steps are present in the code. If any step is missing, add it immediately.

## Background

openpyxl has a known limitation where loading and saving workbooks that contain external links (formulas referencing other workbooks, cached external data connections, or data source references) can corrupt the external link XML entries inside the .xlsx archive. Even workbooks that did not originally have external links can end up with broken entries in `[Content_Types].xml` or orphaned files under `xl/externalLinks/` after openpyxl processes them.

The result is that Excel prompts the user with: "We found a problem with some content in '<filename>'. Do you want us to try to recover as much as we can?" The repair log typically shows: "Repaired Records: External formula reference from /xl/externalLinks/externalLink1.xml part."

## Required Steps — ALL Must Be Present

### Step 1. When loading existing workbooks, use `keep_links=False`

Whenever a script loads an existing `.xlsx` file with `openpyxl.load_workbook()`, pass `keep_links=False` to discard external link data that openpyxl cannot reliably re-serialise:

```python
from openpyxl import load_workbook

wb = load_workbook("input.xlsx", keep_links=False)
```

Only omit `keep_links=False` if the script genuinely needs to read and preserve external link targets, and in that case add a comment explaining why.

### Step 2. Clear residual external links before saving

Before calling `wb.save()`, clear any external links that may have accumulated on the workbook object:

```python
wb._external_links = []
wb.save("output.xlsx")
```

### Step 3. Post-save ZIP-level repair of the .xlsx file

After every `wb.save()` call, run a repair function that opens the saved `.xlsx` as a ZIP archive and removes broken external link artefacts. Include the following utility function (or equivalent) in any module that saves Excel files:

```python
import os
import re
import shutil
import tempfile
import zipfile
from xml.etree import ElementTree as ET

from loguru import logger


def repair_excel_external_links(file_path: str) -> None:
    """Remove broken external link entries from a saved .xlsx file.

    Opens the .xlsx as a ZIP archive, strips out any files under
    xl/externalLinks/, removes their references from [Content_Types].xml
    and xl/_rels/workbook.xml.rels, and fixes duplicate MIME-type entries
    in [Content_Types].xml that can also trigger the repair dialog.

    Parameters
    ----------
    file_path : str
        Path to the .xlsx file to repair in-place.
    """
    if not os.path.isfile(file_path):
        logger.warning("repair_excel_external_links: file not found — {}", file_path)
        return

    ns = {
        "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
        "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    }

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
    os.close(tmp_fd)

    try:
        repaired = False

        with zipfile.ZipFile(file_path, "r") as zin, \
             zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)

                # Skip external link files and their relationships
                if item.filename.startswith("xl/externalLinks"):
                    repaired = True
                    continue

                # Clean [Content_Types].xml
                if item.filename == "[Content_Types].xml":
                    root = ET.fromstring(data)
                    original_count = len(root)

                    # Remove Override entries for externalLinks
                    for elem in root.findall(
                        'ct:Override[@PartName]', ns
                    ):
                        part_name = elem.get("PartName", "")
                        if "externalLinks" in part_name:
                            root.remove(elem)
                            repaired = True

                    # Fix duplicate Default entries (e.g. text/xml vs
                    # application/xml for the xml extension)
                    seen_extensions: dict[str, ET.Element] = {}
                    duplicates: list[ET.Element] = []
                    for elem in root.findall("ct:Default", ns):
                        ext = elem.get("Extension", "").lower()
                        if ext in seen_extensions:
                            duplicates.append(elem)
                            repaired = True
                        else:
                            seen_extensions[ext] = elem
                    for dup in duplicates:
                        root.remove(dup)

                    data = ET.tostring(root, xml_declaration=True, encoding="UTF-8")

                # Clean workbook.xml.rels
                if item.filename == "xl/_rels/workbook.xml.rels":
                    root = ET.fromstring(data)
                    for elem in list(root):
                        target = elem.get("Target", "")
                        if "externalLinks" in target:
                            root.remove(elem)
                            repaired = True

                    data = ET.tostring(root, xml_declaration=True, encoding="UTF-8")

                zout.writestr(item, data)

        if repaired:
            shutil.move(tmp_path, file_path)
            logger.info("Repaired external links in {}", file_path)
        else:
            os.unlink(tmp_path)
            logger.debug("No external link repair needed for {}", file_path)

    except Exception:
        logger.exception("Failed to repair external links in {}", file_path)
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
```

### Step 4. Call the repair function immediately after every save

Every place that calls `wb.save(path)` must be followed by `repair_excel_external_links(path)`:

```python
wb._external_links = []
wb.save(output_path)
repair_excel_external_links(output_path)
```

### Step 5. Wrapper pattern for centralised use

If the project has a shared Excel utilities module (e.g. `excel_formatter.py`), add a convenience function that combines the save and repair steps:

```python
def save_workbook(wb: Workbook, file_path: str) -> None:
    """Save an openpyxl workbook and repair external links."""
    wb._external_links = []
    wb.save(file_path)
    repair_excel_external_links(file_path)
    logger.info("Saved workbook to {}", file_path)
```

Then use `save_workbook(wb, path)` everywhere instead of calling `wb.save()` directly.

### Step 6. Pandas integration

When using `pandas.DataFrame.to_excel()` or `pandas.ExcelWriter()`, the repair function must be called after the file is written:

```python
df.to_excel(output_path, index=False, engine="openpyxl")
repair_excel_external_links(output_path)
```

Or with ExcelWriter:

```python
with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
    df.to_excel(writer, index=False)
# Repair AFTER the context manager closes the file
repair_excel_external_links(output_path)
```

## Pre-Completion Checklist

Before marking any task as complete that involves `.xlsx` file output, verify:

- [ ] Every `load_workbook()` call uses `keep_links=False` (or has an explicit comment explaining why not)
- [ ] Every `wb.save()` call is preceded by `wb._external_links = []`
- [ ] Every `wb.save()` call is followed by `repair_excel_external_links()`
- [ ] Every `df.to_excel()` call is followed by `repair_excel_external_links()`
- [ ] Every `pd.ExcelWriter()` usage is followed by `repair_excel_external_links()` after the writer closes
- [ ] The `repair_excel_external_links()` function is defined or imported in the module

## When This Skill Does NOT Apply

- CSV, JSON, or other non-Excel output formats
- Read-only operations that never call `.save()`
- Scripts that intentionally need to preserve valid external workbook links (rare; add an explicit comment explaining why)
