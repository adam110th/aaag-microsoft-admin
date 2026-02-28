When Claude Code creates or updates code, ensure cross-platform compatibility between Linux and Windows. This applies to all generated scripts, utilities, and application code.

## Required Behaviour

1. **File paths** — Use `os.path.join()`, `pathlib.Path`, or equivalent cross-platform path handling instead of hardcoded forward slashes or backslashes. Never assume a specific path separator.

2. **Software and library locations** — Do not hardcode platform-specific paths for software, libraries, fonts, or system utilities (e.g. `/usr/bin/`, `C:\Windows\Fonts\`). Use environment variables, runtime detection, or configuration to resolve locations. If a required resource (such as a font file) may not be available on all platforms, download or bundle it into a directory within the repository so it is available regardless of platform.

3. **Line endings** — When writing files, be explicit about line endings where it matters. Use `newline=""` in Python's `open()` for CSV files. Do not assume `\n` will behave identically on all platforms.

4. **Shell commands** — If the script invokes shell commands, use cross-platform alternatives or provide platform-specific branches (e.g. `platform.system()` checks). Avoid Unix-only commands like `chmod`, `grep`, or `sed` without Windows fallbacks.

5. **Temporary files and directories** — Use `tempfile` module (Python) or equivalent cross-platform temporary file APIs instead of hardcoding `/tmp/` or other platform-specific temp directories.

## When This Skill Applies

- Every time Claude Code generates or modifies code that interacts with the file system, invokes external programs, or references platform-specific resources.
