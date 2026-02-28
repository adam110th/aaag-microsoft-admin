# CLAUDE.md — Claude Code Project Configuration

> **MANDATORY — SESSION START CHECKS — EXECUTE BEFORE ANY OTHER OUTPUT**
>
> At the start of **every** new session, you MUST perform the following
> checks **before** responding to the user's first message or doing any
> other work. Do NOT skip these steps. Do NOT address the user's task
> first. Complete all checks, report the summary, and only then proceed.
>
> 1. **Git sync** — If the current directory is a Git repository, run
>    `git fetch --all --prune` and compare the local branch with its
>    upstream. Report whether the branch is up to date, behind, ahead, or
>    diverged. Warn about uncommitted changes. If incoming remote changes
>    modified any file inside `.claude/` (skills, settings, CLAUDE.md),
>    notify the user and offer to review repo files for compliance and
>    automatically update affected files.
> 2. **Python venv** — Detect and activate any virtual environment
>    (`venv/`, `.venv/`, `env/`). If none exists, ask the user if one
>    should be created.
> 3. **Pip upgrade** — After venv activation, check whether pip is
>    outdated and upgrade it automatically.
> 4. **Summary** — Report a brief summary of all checks to the user.
>
> See `.claude/default-skills/session-start-checks.md` for full details.

---

This file documents the Claude Code setup for this repository so that any
contributor (human or AI) can understand, maintain, and replicate it.

---

## Default Skill Rules

The following rules apply to **every** Claude Code session in this
repository. They are loaded automatically because they are part of this
CLAUDE.md file.

### Maintenance

**Repository knowledge map** — When reviewing or working on a repository,
create or update an internal knowledge map at `.claude/codebase-knowledge.md`
that stores structured information about the repository (architecture,
entry points, key components, dependencies, patterns, testing, and CI/CD).
Create it on first session; update it after tasks that change the codebase.
This enables Claude Code to understand and navigate the codebase more
quickly in future sessions.

**Auto-update common files** — After completing any task, check if any of
the repository's common files need updating (e.g. `.gitignore`, CI configs).
Check if the README.md needs updating. If there are any README.md files in
folders and subfolders that need updating, do them as well. For Python
projects, check if `requirements.txt` needs updating. For other languages,
check their equivalent project-specific common files and configuration.

**Create README files** — After completing all tasks, check if there is a
README.md file in the repository root. If there is none, create one with all
of the repository details. If there are folders and subfolders that would
benefit from a README.md, create ones in there too.

**Pin dependency versions** — When creating or updating dependency files
(`requirements.txt`, `package.json`, `Gemfile`, `go.mod`, `Cargo.toml`,
etc.), pin dependencies to specific versions or at minimum use
compatible-release specifiers (e.g. `~=` in Python, `^` in npm) rather than
leaving versions unpinned or using `>=` without an upper bound. For
`requirements.txt`, use `==` for direct dependencies. For `package.json`,
use `^` (caret) ranges. When adding a new dependency, check the current
latest stable version and pin to that.

**Create `.gitignore` file** — When working on a repository, if no
`.gitignore` file is present, create one tailored to the languages and
frameworks used in the project before any other work begins. Include rules
for IDE directories, OS-generated files, secrets files (`.env`, `*.pem`,
`*.key`), and a clearly marked custom ignores section at the bottom that
must be retained on future updates.

**Consolidate requirements files** — After completing any task that adds,
removes, or updates dependencies in a subfolder's `requirements.txt`, merge
all subfolder dependencies into the root-level `requirements.txt`. The root
file is the single source of truth. Preserve section comments indicating
which subfolder each group originated from. De-duplicate packages and keep
the highest pinned version.

### Compatibility

**Cross-platform compatibility** — Ensure generated code has cross
compatibility with both Linux and Windows. For example software library
locations, program locations, font locations. If needed, download the
required files into relevant folders in the repository, so they are
available regardless of platform.

**Encoding handling** — When creating or updating scripts that read or write
text files, always specify the encoding explicitly rather than relying on
platform defaults. Use UTF-8 as the default encoding. In Python, always pass
`encoding="utf-8"` to `open()`. When reading files from unknown sources,
handle encoding errors gracefully (e.g. `errors="replace"` in Python)
rather than letting the script crash on malformed input.

**Python version** — When creating or updating Python scripts, the minimum
Python version is 3.14+. All packages and modules must be compatible with
Python 3.14 and the Windows operating system. Before adding a dependency to
`requirements.txt`, verify the package supports both Python 3.14+ and
Windows. Use PEP 508 environment markers for platform-specific dependencies.
At session start in Python projects, check whether a newer stable Python
version is available. If so, ask the user if they want to upgrade. Before
upgrading, verify all packages have wheels for the new version, check for
deprecated or changed APIs in the codebase, and present options: keep
current versions, upgrade and refactor, or partial upgrade. After
upgrading, ask the user if the AAAG-AU/.dotfiles-github-defaults skill
should be updated to push the version change to all repositories.

### Error Handling

**File-locked errors** — When creating scripts that open files on the local
file system, include a prompt so that if the file is locked for editing, the
user is notified that the file is locked and asked to close it and hit
enter. If the file is still locked, loop back through the prompt until the
script can proceed.

**File-not-found errors** — When writing scripts that access local files, if
a file is not found, notify the user and prompt them to input an alternate
file location, or ask if they would like to quit. Continue looping the
prompt if the newly inputted file is not found as well.

**Graceful error logging** — Ensure errors are logged with meaningful
context. Error messages should describe what operation failed, provide
relevant details (file paths, URLs, input values), and where possible
suggest corrective action. Avoid silent failures — do not use bare
except/catch blocks that swallow errors without logging. For scripts with
multiple steps, include which step failed.

**Keyboard interrupts** — Ensure scripts allow for graceful exit by keyboard
interrupt (Ctrl+C).

### Security

**Input sanitization** — For code creation, whenever a user is prompted for
a response, always sanitize the input and verify the response is of an
expected response type.

**Sensitive data protection** — Never hardcode sensitive data such as API
keys, tokens, passwords, database connection strings, private keys, or
other credentials directly in source code. Use environment variables,
`.env` files listed in `.gitignore`, or secret management tools. When
generating example code that requires credentials, use clearly marked
placeholders (e.g. `YOUR_API_KEY_HERE`) and include a comment explaining
how to set the real value via environment variables. If a `.env` file is not
already in `.gitignore`, add it. Never commit files that contain real
credentials.

**Env file quoting** — When creating or updating `.env`, `.env.example`, or
any dotenv-format file, all variable values MUST be wrapped in single
quotes. This prevents `#` characters in values (common in API keys and
tokens) from being interpreted as inline comments, which silently truncates
the value. Single quotes also prevent unintended `$` variable
interpolation. Apply this to both `.env` and `.env.example` files. When
updating an existing file with unquoted values, fix all values, not just
the ones being changed.

### Reliability

**Timeout handling** — When creating or updating scripts that make network
requests, API calls, database queries, subprocess invocations, or other
external I/O operations, always include reasonable timeout values. Use
language-appropriate timeout mechanisms. Choose sensible defaults — typically
30 seconds for HTTP requests and 60 seconds for longer operations — and make
them configurable where appropriate.

**Resource cleanup** — When creating or updating scripts that open files,
database connections, network sockets, subprocess handles, or other system
resources, ensure they are properly closed and released after use. Use
context managers (`with` statements) in Python, `try-with-resources` in
Java, `using` in C#, `defer` in Go, or `try/finally` as a fallback.

### Code Quality

**Think before coding** — Do not jump straight into writing code. State
assumptions explicitly before starting work. If the task is ambiguous,
present multiple interpretations and ask which one is intended rather than
silently picking one. Push back when a simpler approach exists — suggest it
before implementing the more complex option. If something is unclear, stop
and name exactly what is confusing rather than guessing and proceeding.

**Simplicity first** — Write the minimum code that solves the problem. If a
solution can be expressed in fewer lines without sacrificing readability,
prefer the shorter version. Do not add layers of abstraction, configuration,
or generalization beyond what the task requires. If 200 lines could be 50,
rewrite it. Resist the urge to over-engineer — solve the problem at hand,
not hypothetical future problems.

### Debugging

**Systematic debugging** — When debugging issues, bugs, errors, or
unexpected behavior, follow a structured four-phase methodology: (1) Gather
evidence — reproduce the issue, read the traceback, check recent changes,
collect context. (2) Form hypotheses — state 2-3 ranked hypotheses with
evidence for/against each. (3) Test hypotheses — design minimal tests, one
variable at a time, use targeted logging. (4) Fix and verify — write a
failing test, make the minimal fix, run full test suite, remove debug
artifacts. Never shotgun-debug or fix symptoms without understanding root
cause. See `.claude/default-skills/systematic-debugging.md` for full
details.

### Testing

**Testing patterns** — When creating or updating tests, follow pytest
conventions: use TDD (red-green-refactor), Arrange-Act-Assert structure,
factory functions (`make_<entity>(**overrides)`), and `@pytest.fixture` for
shared setup. Mock external boundaries (APIs, databases, filesystems), not
internal code. Use `@pytest.mark.parametrize` for multiple inputs. One
logical assertion per test. Place tests in `tests/` mirroring `src/`
structure. See `.claude/default-skills/testing-patterns.md` for full details.

### Verification

**Verification before completion** — Before claiming any task is complete,
follow this protocol: (1) Run `pytest` and confirm all tests pass. (2) Run
`ruff check .` and `pyright`. (3) Re-read the original request and check
off each requirement. (4) Test edge cases. (5) Run the full test suite for
regressions. (6) Review your own diff with `git diff` — look for debug
prints, commented-out code, TODOs, hardcoded values, missing encoding args.
(7) Verify cross-platform compatibility. Never declare done without evidence.
See `.claude/default-skills/verification-before-completion.md` for full
details.

### Workflow

**Parallel agent orchestration** — When a coding task involves 3 or more
independent files, functions, or components, use the Task tool to split the
work across parallel sub-agents. For larger tasks (5+ files or multi-step
implementations), operate as a **head agent**: decompose the task into
independent work units, dispatch sub-agents in parallel for units with no
shared dependencies, and run dependent units sequentially. After all agents
complete, review every output against the original user request — check that
every function, endpoint, and feature is fully implemented, not stubbed or
skipped. If anything is missing, deploy additional agents to fill the gaps.
Continue this review-and-deploy cycle until all requirements are satisfied.
Never declare the task complete until every requested feature is fully
implemented.

### Excel

**Excel external link repair (MANDATORY)** — Every time a Python script is
created or updated that saves Excel workbooks (.xlsx) using openpyxl or any
library built on it (including pandas with the openpyxl engine), ALL of the
following steps MUST be present: (1) use `keep_links=False` when calling
`load_workbook()`, (2) set `wb._external_links = []` before every
`wb.save()`, (3) call `repair_excel_external_links()` after every save, and
(4) include the ZIP-level repair utility function that strips orphaned
`xl/externalLinks/` entries from the archive. This applies to any script
that imports openpyxl, calls `wb.save()`, uses `DataFrame.to_excel()`, or
uses `ExcelWriter`. No exceptions. See
`.claude/default-skills/excel-repair-lookup-links.md` for the full repair
function and implementation details.

### Web Development

**Web page defaults** — When generating or updating a webpage or website,
create or verify the following files: (1) `.htaccess` with AI crawler
blocking, hotlink prevention, gzip compression, ETag removal, security
headers, and backup/config file blocking; (2) `robots.txt` blocking AI
crawlers by default; (3) `favicon.ico` reflecting the site theme; (4)
custom error pages (400, 401, 403, 404, 500) styled consistently with the
site. If these files already exist, verify they include the required
defaults and offer to add any missing items.

### Documentation

**Document citations** — When generating a spreadsheet or word-processing
document that incorporates data from external sources, always include full
references for those sources. For word-processing documents, add a
"References" section at the end of the document. For spreadsheets, create a
separate "References" tab listing each external source in a tabular format,
and annotate data cells with notes pointing to the corresponding reference.
If no external sources are used, no references section or tab is needed.

---

## Project Skill Rules

In addition to the default skill rules above, this repository may contain
**project-specific skills** in `.claude/project-skills/`. At the start of
every session, scan the `.claude/project-skills/` directory for any `.md`
files (excluding `README.md`). Read each file and follow the skill
instructions contained within. These project skills are loaded dynamically —
adding a new `.md` file to the folder is all that is needed to activate a
new project skill.

Project skills take precedence over default skills when there is a conflict
for this specific repository.

---

## Claude Code Configuration (`.claude/`)

### Directory Layout

```
.claude/
├── CLAUDE.md                  # This file — project instructions & skill rules
├── settings.json              # Project-level Claude Code settings (hooks, env, permissions)
├── settings.md                # Human-readable hook documentation
├── .gitignore                 # Ignores local/personal Claude Code files
├── agents/                    # Custom AI agents with focused purposes
│   ├── code-reviewer.md       # Python-focused code review agent
│   └── github-workflow.md     # Git commit, branch, and PR workflow agent
├── commands/                  # Slash commands (/command-name)
│   ├── onboard.md             # Deep task exploration and context building
│   ├── pr-review.md           # PR review using project standards
│   ├── pr-summary.md          # Generate PR description from diff
│   ├── code-quality.md        # Run code quality checks on a directory
│   ├── docs-sync.md           # Check if documentation matches code
│   └── ticket.md              # JIRA/Linear ticket workflow (read → implement → update)
├── hooks/                     # Hook scripts for automated workflows
│   ├── skill-eval.sh          # Bash wrapper for skill evaluation
│   ├── skill-eval.py          # Python skill matching engine
│   ├── skill-rules.json       # Pattern matching configuration
│   └── skill-rules.schema.json # JSON schema for skill rules validation
├── default-skills/            # Organization-wide skill definitions (plain .md files)
│   ├── README.md
│   ├── repository-knowledge-map.md
│   ├── auto-update-github-common-files.md
│   ├── create-a-readme-file.md
│   ├── cross-platform-compatibility.md
│   ├── dependency-pinning.md
│   ├── document-citations.md
│   ├── encoding-handling.md
│   ├── file-locked-error.md
│   ├── file-not-found.md
│   ├── graceful-error-logging.md
│   ├── keyboard-interrupts.md
│   ├── resource-cleanup.md
│   ├── sensitive-data-protection.md
│   ├── think-before-coding.md
│   ├── timeout-handling.md
│   ├── user-prompt-security.md
│   ├── parallel-agent-orchestration.md
│   ├── excel-repair-lookup-links.md
│   ├── create-a-gitignore-file.md
│   ├── consolidate-requirements.md
│   ├── python-version.md
│   ├── web-page-defaults.md
│   ├── env-file-quoting.md
│   ├── session-start-checks.md
│   ├── systematic-debugging.md
│   ├── testing-patterns.md
│   └── verification-before-completion.md
└── project-skills/            # Project-specific skill definitions (plain .md files)
    └── README.md
```

### Repository-Level Files

```
├── .mcp.json                  # MCP server configuration template (JIRA, GitHub, Slack, etc.)
├── setup-claude.sh            # Setup script — auto-detects project type (Linux/macOS)
├── setup-claude.ps1           # Setup script — auto-detects project type (Windows)
├── CLAUDE-CODE-POLICY.md      # Internal policy document
├── .github/
│   ├── org-setup.md           # Org-level provisioning guide
│   └── workflows/
│       ├── validate-claude-config.yml              # CI check for .claude/ compliance
│       ├── auto-provision-claude.yml               # Auto-provision on new repo creation
│       ├── sync-skills.yml                         # Weekly skills sync workflow
│       ├── sync-claude-config.yml                   # Push-triggered full .claude/ sync to all org repos
│       ├── pr-claude-code-review.yml               # Auto PR review with Claude
│       ├── scheduled-claude-code-docs-sync.yml     # Monthly documentation sync
│       ├── scheduled-claude-code-quality.yml       # Weekly code quality review
│       └── scheduled-claude-code-dependency-audit.yml  # Biweekly dependency audit
└── skills-registry/
    ├── registry.json          # Central skill metadata & versions
    ├── README.md              # Registry documentation
    └── sync-skills.sh         # Script to sync full .claude/ config to a target repo
```

### `settings.json`

Located at `.claude/settings.json`, this file controls project-level
Claude Code behavior:

| Section | Purpose |
|---------|---------|
| `includeCoAuthoredBy` | Automatically adds Co-Authored-By trailer to commits. |
| `env` | Environment variables: `INSIDE_CLAUDE_CODE` flag, bash timeout settings. |
| `hooks` | Automated workflows: skill evaluation on prompt submit, branch protection on edit, auto-format/test/typecheck on file save. See `.claude/settings.md` for details. |
| `enabledPlugins` | Plugins enabled for all contributors. When a contributor trusts the repository, these plugins auto-install from the `claude-plugins-official` marketplace. |
| `permissions.allow` | Pre-approved tools and commands so Claude can work without repeated approval prompts. Includes file I/O tools, git, GitHub CLI, pip, ruff, pyright, pytest, and basic shell commands. |
| `permissions.deny` | Explicitly blocked dangerous patterns: `rm -rf /`, `sudo`, `chmod 777`, piped-curl/wget execution. |
| `projectContext` | Metadata about this project (language, Python version, entry point, dependency file) to give Claude relevant context. |

### Plugins

The following plugins from the `claude-plugins-official` marketplace are
configured at the project level via `enabledPlugins` in `settings.json`.
When a contributor trusts this repository, Claude Code will auto-install
the enabled plugins.

| Plugin | Status | Purpose |
|--------|--------|---------|
| `context7` | Enabled | Fetches up-to-date library documentation |
| `code-review` | Enabled | Automated code review capabilities |
| `github` | **Disabled** | Enhanced GitHub integration |
| `code-simplifier` | Enabled | Simplifies and refines code for clarity and maintainability |
| `frontend-design` | Enabled | Production-grade frontend interface generation |
| `feature-dev` | Enabled | Guided feature development with architecture focus |
| `superpowers` | Enabled | Advanced workflow skills (brainstorming, debugging, TDD, etc.) |
| `ralph-loop` | **Disabled** | Autonomous agent loop for complex tasks |
| `typescript-lsp` | Enabled | TypeScript language server integration |
| `playwright` | Enabled | Browser automation and testing |
| `commit-commands` | Enabled | Git commit, push, and PR workflows |
| `serena` | **Disabled** | Semantic code analysis and editing tools |
| `security-guidance` | Enabled | Security best practices and vulnerability detection |
| `pr-review-toolkit` | Enabled | Comprehensive PR review with specialized agents |
| `pyright-lsp` | Enabled | Python type checking via Pyright language server |
| `claude-md-management` | Enabled | CLAUDE.md auditing and improvement |

### Default Skills

Skills are reusable behavior definitions stored as plain `.md` files in
`.claude/default-skills/`. Their contents are included in the **Default
Skill Rules** section above so they are loaded into every Claude Code
session automatically.

| Skill | What It Does |
|-------|-------------|
| `repository-knowledge-map` | Creates and maintains a `.claude/codebase-knowledge.md` file for faster codebase understanding |
| `auto-update-github-common-files` | Keeps `.gitignore`, CI configs, and other standard GitHub files consistent |
| `create-a-readme-file` | Creates README.md for repositories and directories that lack one |
| `cross-platform-compatibility` | Ensures code works on Linux, macOS, and Windows |
| `dependency-pinning` | Pins dependency versions for reproducible builds |
| `document-citations` | Adds source references to generated spreadsheets and documents |
| `encoding-handling` | Handles file encoding explicitly, defaulting to UTF-8 |
| `file-locked-error` | Graceful recovery from file-lock errors |
| `file-not-found` | Smart recovery when referenced files are missing |
| `graceful-error-logging` | Errors are logged with meaningful context |
| `keyboard-interrupts` | Clean handling of Ctrl+C and interrupt signals |
| `resource-cleanup` | Files, connections, and resources are properly released |
| `sensitive-data-protection` | Prevents hardcoding secrets and credentials |
| `think-before-coding` | Forces explicit reasoning, surfaces tradeoffs, and keeps solutions minimal |
| `timeout-handling` | Adds timeouts to network requests and external operations |
| `user-prompt-security` | Guards against prompt injection and unsafe inputs |
| `parallel-agent-orchestration` | Splits larger tasks across parallel sub-agents with a head agent for completeness verification |
| `excel-repair-lookup-links` | Mandatory Excel external link repair for all openpyxl/pandas .xlsx saves |
| `create-a-gitignore-file` | Creates tailored `.gitignore` files for repositories that lack one |
| `consolidate-requirements` | Merges subfolder `requirements.txt` files into the root dependency file |
| `python-version` | Enforces Python 3.14+ with version upgrade checks and compatibility assessment |
| `web-page-defaults` | Creates `.htaccess`, `robots.txt`, favicon, and error pages for web projects |
| `env-file-quoting` | Wraps all `.env` variable values in single quotes to prevent `#` truncation |
| `session-start-checks` | Auto-syncs Git repos, activates Python venvs, and upgrades pip at session start |
| `systematic-debugging` | Four-phase debugging: gather evidence, form hypotheses, test, fix and verify |
| `testing-patterns` | Python testing with pytest: TDD, fixtures, factory functions, mocking, parametrize |
| `verification-before-completion` | Evidence-based completion protocol: tests, linting, type checks, diff review |

### Agents

Custom AI agents with focused purposes, stored in `.claude/agents/`.

| Agent | What It Does |
|-------|-------------|
| `code-reviewer` | Python-focused code review with structured checklist (security, encoding, types, errors) |
| `github-workflow` | Git workflow: branch naming, conventional commits, PR creation |

### Commands

Custom slash commands invoked with `/command-name`, stored in `.claude/commands/`.

| Command | What It Does |
|---------|-------------|
| `/onboard` | Deep task exploration — builds comprehensive context for complex tasks |
| `/pr-review` | Reviews a PR using the code-reviewer agent's standards |
| `/pr-summary` | Generates a PR description from the current branch diff |
| `/code-quality` | Runs code quality checks (ruff, pyright) on a directory |
| `/docs-sync` | Checks if documentation matches recent code changes |
| `/ticket` | Full ticket workflow: read ticket, implement, test, create PR, update ticket |

### Hooks

Automated workflows triggered by Claude Code events, stored in `.claude/hooks/`.

| Hook | Event | What It Does |
|------|-------|-------------|
| Skill evaluation | `UserPromptSubmit` | Analyzes prompts and suggests relevant default skills |
| Branch protection | `PreToolUse` | Blocks file edits on main/master branch |
| Python auto-format | `PostToolUse` | Runs `ruff format` and `ruff check --fix` on edited `.py` files |
| Auto-install deps | `PostToolUse` | Runs `pip install -r requirements.txt` when requirements change |
| Auto-run tests | `PostToolUse` | Runs `pytest` on edited test files |
| Python type check | `PostToolUse` | Runs `pyright` on edited `.py` files |

### MCP Servers

Template MCP server configurations in `.mcp.json` for external integrations.

| Server | What It Does |
|--------|-------------|
| `github` | Enhanced GitHub integration |
| `postgres` | Database querying |
| `slack` | Team communication automation |
| `sentry` | Error monitoring integration |
| `jira` | JIRA issue tracking |
| `linear` | Linear issue tracking |
| `notion` | Knowledge base integration |
| `memory` | Persistent context across sessions |

### Project Skills

Project-specific skills are stored as plain `.md` files in
`.claude/project-skills/`. Unlike default skills, these are **not** managed
centrally and are unique to the repository they live in. They are loaded
dynamically at the start of every session — adding a new `.md` file to the
folder automatically activates the skill without any other configuration
changes.

Use `project-skills/` for repository-specific conventions, patterns,
workflows, or domain knowledge that Claude should always consider when
working in this project. See `.claude/project-skills/README.md` for
detailed guidance.

---

## Replicating This Setup to Other Repositories

The `.claude/` folder is self-contained and designed to be portable:

1. **Copy the folder:**
   ```bash
   cp -r .claude/ /path/to/other-repo/.claude/
   ```

2. **Update `projectContext`** in `settings.json` to match the target
   project (language, entry point, dependency file, etc.).

3. **Adjust `permissions.allow`** if the target project uses different
   toolchains (e.g., add `Bash(npm *)` for Node.js projects, `Bash(cargo *)`
   for Rust, etc.).

4. **Commit the `.claude/` folder** to the target repo so all contributors
   get the same configuration.

The skill files are language-agnostic and work across any project type.

---

## Company-Wide Policy

> Standardize this `.claude/` configuration as a company-wide policy applied
> to all repositories.

### Recommended steps:

- [ ] Create a shared **template repository** (e.g., `org/claude-config-template`)
  containing the canonical `.claude/` folder with `settings.json` and
  default skills
- [x] Write a **setup script** (`setup-claude.sh`) that copies the template
  `.claude/` folder into any repo and adjusts `projectContext` based on
  detected project type (Python, Node, Go, etc.)
  — See [`setup-claude.sh`](../setup-claude.sh)
- [x] Add a **CI check** (GitHub Action or pre-commit hook) that validates
  every repository has a `.claude/` folder matching the approved baseline
  — See [`.github/workflows/validate-claude-config.yml`](../.github/workflows/validate-claude-config.yml)
- [x] Publish an **internal policy document** covering:
  - Required default skills for all repos
  - Approved permission allow/deny lists per project type
  - Process for proposing and reviewing new default skills
  - Versioning strategy for skill files
  — See [`CLAUDE-CODE-POLICY.md`](../CLAUDE-CODE-POLICY.md)
- [x] Consider a **GitHub App or organization-level config** that
  automatically provisions `.claude/` on new repository creation
  — See [`.github/workflows/auto-provision-claude.yml`](../.github/workflows/auto-provision-claude.yml)
  and [`.github/org-setup.md`](../.github/org-setup.md)
- [x] Set up a **central skills registry** so teams can share and discover
  skills across the organization
  — See [`skills-registry/`](../skills-registry/) and
  [`.github/workflows/sync-skills.yml`](../.github/workflows/sync-skills.yml)
- [x] Set up **automatic push-triggered sync** to mirror the full `.claude/`
  config to all organization repos whenever any file under `.claude/`
  changes. Syncs settings, skills, agents, commands, and hooks. Repos
  without `.claude/` are bootstrapped. `project-skills/` contents are
  never overwritten (folder + README created if missing)
  — See [`.github/workflows/sync-claude-config.yml`](../.github/workflows/sync-claude-config.yml)

