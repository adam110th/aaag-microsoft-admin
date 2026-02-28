When Claude Code creates or updates scripts that read or write text files, the encoding MUST be specified explicitly. Never rely on platform defaults.

## Required Behaviour

1. **Default to UTF-8** — Use UTF-8 as the encoding unless there is a specific, documented reason to use another encoding.

2. **Python** — Always pass `encoding="utf-8"` to `open()`:
   ```python
   with open("file.txt", "r", encoding="utf-8") as f:
       content = f.read()
   ```

3. **Other languages** — Use the equivalent explicit encoding parameter (e.g. `StandardCharsets.UTF_8` in Java, `{ encoding: "utf-8" }` in Node.js).

4. **Unknown sources** — When reading files from unknown or external sources, handle encoding errors gracefully rather than letting the script crash:
   ```python
   with open("file.txt", "r", encoding="utf-8", errors="replace") as f:
       content = f.read()
   ```

5. **CSV files** — When writing CSV files, use `newline=""` in Python's `open()` to prevent double line endings on Windows.

## Why

The default system encoding differs between Linux (usually UTF-8), Windows (usually CP-1252 or UTF-8 depending on locale), and macOS (UTF-8). Relying on platform defaults causes mojibake and inconsistent behaviour across environments.

## When This Skill Applies

- Every script that reads from or writes to text files.
