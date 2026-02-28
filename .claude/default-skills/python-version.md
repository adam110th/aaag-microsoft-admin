When Claude Code creates or updates Python scripts, the minimum Python version MUST be 3.14 or higher.

## Required Behaviour

1. **Language features** — Use Python 3.14+ syntax and features. Do not include compatibility shims or fallbacks for older Python versions unless the user explicitly requests them.

2. **Package compatibility** — All packages and modules used MUST be compatible with Python 3.14 and the Windows operating system. Before adding a dependency to `requirements.txt`, verify that the package has published a wheel or sdist that supports both Python 3.14+ and Windows. If a package does not support Windows, find a cross-platform alternative or flag the incompatibility to the user.

3. **`requirements.txt` markers** — When a dependency requires platform-specific markers (e.g. a Unix-only optional dependency), use PEP 508 environment markers to prevent installation failures on Windows:
   ```
   some-unix-package==1.2.3; sys_platform != "win32"
   ```

4. **Shebang lines** — If including a shebang line, use `#!/usr/bin/env python3` for portability. Do not hardcode a specific Python path.

## Version Upgrade Check

At the start of each session in a Python project, Claude Code MUST check whether a newer stable Python version is available beyond the version specified above (currently 3.14). If a newer stable release exists (e.g. 3.15, 3.16), follow this process:

### 1. Check suppression and notify the user

Before prompting, check whether the user has previously declined this upgrade. Claude Code stores a `python_version_check_declined` timestamp in `.claude/session-memory/` (or equivalent persistent memory). If the user declined within the last 30 days, skip the prompt entirely and continue using the current version silently.

If no recent decline is recorded (or more than 30 days have passed since the last decline), ask the user: *"Python X.Y is now available as a stable release. The current minimum version for this project is 3.14. Would you like to upgrade?"*

If the user declines:
- Record the current date as `python_version_check_declined` along with the version that was offered (e.g. `declined_version: "3.15"`, `declined_date: "2026-02-20"`).
- Do not ask again for at least 30 days.
- If a **different** newer version becomes available (e.g. 3.16 when they previously declined 3.15), the 30-day cooldown resets and the user should be prompted about the new version.

### 2. Compatibility assessment (if user agrees to consider upgrading)

Before upgrading, perform a full compatibility check:

#### a. Package wheel availability
- For every package in `requirements.txt`, check whether a pre-built wheel is available for the new Python version on PyPI.
- If any package does not have a wheel available for the new version, warn the user: *"The following packages do not have wheels for Python X.Y yet: [list]. The upgrade cannot proceed until these are available."*
- If newer versions of those packages do have wheels, check whether upgrading the packages would be safe (see step b).

#### b. Deprecated and changed APIs
- Check for Python standard library changes between the current version and the target version (removed modules, deprecated functions, changed behaviour).
- Scan the existing codebase for usage of any deprecated or removed functions, modules, or patterns.
- Check whether any pinned package versions have known incompatibilities with the new Python version.
- Report all findings to the user with specific file paths and line references.

#### c. Package version upgrades
- If packages need to be upgraded for compatibility, verify that:
  - The newer package versions have published wheels for the new Python version **and** for Windows.
  - The newer package versions do not introduce breaking API changes that would affect the existing codebase.
- If breaking changes are found, list them with specific details (function signatures changed, classes removed, etc.).

### 3. Present options to the user

Based on the assessment, present the user with clear options:

- **Option A: Keep current versions** — No changes. Continue using Python 3.14 and current package versions.
- **Option B: Upgrade Python and update packages** — Upgrade the minimum Python version, update `requirements.txt` with compatible package versions, and refactor any code that uses deprecated or changed APIs. List all code changes that would be made.
- **Option C: Partial upgrade** — If only some packages are blocking, offer to upgrade Python and the compatible packages while keeping the blocking packages pinned, with a note about future upgrading when wheels become available.

### 4. Execute the chosen option

If the user chooses to upgrade:

1. Update the Python version requirement in this skill file (`.claude/default-skills/python-version.md`) and in CLAUDE.md.
2. Update `requirements.txt` with compatible package versions.
3. Refactor any code that uses deprecated or changed APIs, showing the user each change.
4. Run any available tests to verify nothing is broken.

### 5. Upstream skill update

After completing an upgrade, ask the user: *"Would you like to update the Python version skill in AAAG-AU/.dotfiles-github-defaults to push this version change to all repositories?"*

- If the current working repository **is** `AAAG-AU/.dotfiles-github-defaults`, make the update directly.
- If the current working repository is **not** `AAAG-AU/.dotfiles-github-defaults`, advise the user that the default skill in the central repository should be updated separately and provide the repository URL: `https://github.com/AAAG-AU/.dotfiles-github-defaults`

## When This Skill Applies

- Every Python script or project that Claude Code creates or updates.
- The version upgrade check runs once at session start in Python projects.
