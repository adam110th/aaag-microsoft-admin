# Default Skills

This folder contains skill definitions as plain `.md` files. Each file
describes a behavior rule that Claude Code should follow during every
session in this repository.

## How It Works

The skill instructions from these files are included directly in
`.claude/CLAUDE.md` under the **Default Skill Rules** section. Because
Claude Code automatically loads `CLAUDE.md` at the start of every session,
the rules are always active.

The `.md` files in this folder serve as the single source of truth for each
skill's definition. When adding or editing a skill, update both the `.md`
file here and the corresponding entry in `CLAUDE.md`.

## Included Skills

### Session Start

| Skill File | Purpose |
|------------|---------|
| `session-start-checks.md` | Auto-syncs Git repos, activates Python venvs, and upgrades pip at session start |

### Maintenance

| Skill File | Purpose |
|------------|---------|
| `repository-knowledge-map.md` | Creates and maintains `.claude/codebase-knowledge.md` for faster codebase understanding |
| `auto-update-github-common-files.md` | Keeps common GitHub files (e.g., `.gitignore`, CI configs) up to date |
| `create-a-readme-file.md` | Creates README.md files for repositories and subdirectories that lack them |
| `dependency-pinning.md` | Pins dependency versions for reproducible builds |
| `create-a-gitignore-file.md` | Creates tailored `.gitignore` files for repositories that lack one |
| `consolidate-requirements.md` | Merges subfolder `requirements.txt` files into the root dependency file |

### Compatibility

| Skill File | Purpose |
|------------|---------|
| `cross-platform-compatibility.md` | Ensures code works across Linux, macOS, and Windows |
| `encoding-handling.md` | Handles file encoding explicitly, defaulting to UTF-8 |
| `python-version.md` | Enforces Python 3.14+ with version upgrade checks and compatibility assessment |

### Error Handling

| Skill File | Purpose |
|------------|---------|
| `file-locked-error.md` | Handles file-lock errors gracefully during operations |
| `file-not-found.md` | Provides smart recovery when files are missing |
| `keyboard-interrupts.md` | Handles Ctrl+C and interrupt signals cleanly |
| `graceful-error-logging.md` | Ensures errors are logged with meaningful context |

### Security

| Skill File | Purpose |
|------------|---------|
| `user-prompt-security.md` | Guards against prompt injection and unsafe inputs |
| `sensitive-data-protection.md` | Prevents hardcoding secrets and credentials in code |
| `env-file-quoting.md` | Wraps all `.env` variable values in single quotes to prevent `#` truncation |

### Reliability

| Skill File | Purpose |
|------------|---------|
| `timeout-handling.md` | Adds timeouts to network requests and external operations |
| `resource-cleanup.md` | Ensures files, connections, and resources are properly released |

### Code Quality

| Skill File | Purpose |
|------------|---------|
| `think-before-coding.md` | Forces explicit reasoning, surfaces tradeoffs, and keeps solutions minimal |
| `systematic-debugging.md` | Four-phase debugging methodology: gather evidence, form hypotheses, test, fix and verify |
| `testing-patterns.md` | Python testing patterns with pytest: TDD, fixtures, factory functions, mocking, parametrize |
| `verification-before-completion.md` | Evidence-based completion protocol requiring tests, linting, type checks, and diff review |

### Documentation

| Skill File | Purpose |
|------------|---------|
| `document-citations.md` | Adds source references to generated spreadsheets and word-processing documents |

### Workflow

| Skill File | Purpose |
|------------|---------|
| `parallel-agent-orchestration.md` | Splits larger tasks across parallel sub-agents with a head agent for completeness verification |

### Excel

| Skill File | Purpose |
|------------|---------|
| `excel-repair-lookup-links.md` | Mandatory Excel external link repair for all openpyxl/pandas .xlsx saves |

### Web Development

| Skill File | Purpose |
|------------|---------|
| `web-page-defaults.md` | Creates `.htaccess`, `robots.txt`, favicon, and error pages for web projects |

## Adding New Skills

1. Create a `.md` file in this directory with the skill instructions
2. Add the corresponding rule text to the **Default Skill Rules** section
   in `.claude/CLAUDE.md`
3. Commit and push — the skill will be active for all Claude Code sessions

## Project-Specific Skills

For skills that only apply to a particular project (not organization-wide),
use the `.claude/project-skills/` folder instead. Project skills are loaded
dynamically — simply drop a `.md` file in that folder and it becomes active.
See `.claude/project-skills/README.md` for details.

| Folder | Scope | Centrally Managed |
|--------|-------|-------------------|
| `default-skills/` | All repositories | Yes |
| `project-skills/` | Single repository | No |

## Replicating to Other Repositories

Copy the entire `.claude/` folder (including `settings.json`, `CLAUDE.md`,
`default-skills/`, and `project-skills/`) into any repository root. Adjust
`projectContext` in `settings.json` to match the target project's language
and entry point.
