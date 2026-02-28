# Codebase Knowledge Map — aaag-microsoft-admin

## Overview

Microsoft 365 Admin Toolkit — a modular CLI for managing Microsoft 365 resources via the Microsoft Graph API. Features auto-discovery of tools, per-tool authentication scopes, and shared infrastructure for retry/pagination/file handling.

## Architecture

Modular toolkit with convention-based tool discovery:

```
src/
  core/                      Shared infrastructure
    config.py                Environment loading, constants (GRAPH_BASE, timeouts)
    auth.py                  MSAL auth: client credentials + delegated (browser)
    graph_client.py          GraphClient class: get(), delete(), get_paged() with retry
    utils.py                 File I/O helpers, sanitize_filename, parse_range_selection
  tools/                     Tool packages (auto-discovered)
    _base.py                 ToolDefinition frozen dataclass
    teams_chat_export/       Export Teams chat messages and media
      tool.py                Fetch messages, download media, save JSON/MD/CSV
    enterprise_apps/         Manage Azure AD service principals
      tool.py                List/inspect/delete enterprise applications
  main.py                    Menu launcher with pkgutil-based discovery
  __main__.py                Entry point for python -m src
```

## Entry Point

```bash
python -m src              # launches interactive menu
```

## Key Components

### Core

| Module | Purpose |
|--------|---------|
| `config.py` | `load_environment(extra_required, extra_optional)`, constants (`GRAPH_BASE`, `GRAPH_BETA`) |
| `auth.py` | `get_client_credentials_token(env, scopes)`, `get_delegated_token(env, scopes)` |
| `graph_client.py` | `GraphClient` class: `get()`, `post()`, `patch()`, `delete()`, `get_paged()` with retry (429/5xx), pagination, error parsing |
| `utils.py` | `write_with_lock_check()`, `save_json()`, `sanitize_filename()`, `parse_range_selection()` |

### Tools

| Tool | Module | Permissions |
|------|--------|-------------|
| Teams Chat Export | `src.tools.teams_chat_export` | App: `Chat.Read.All`; Delegated: `Chat.Read`, `Chat.ReadBasic` |
| Enterprise Apps | `src.tools.enterprise_apps` | App: `Application.Read.All` (read), `Application.ReadWrite.All` (delete, on demand). Sorting by name/created/cert-expiry/assignments. Detail view shows Roles and Administrators (app roles + granted API permissions), users/groups, SSO, provisioning. |

### Tool Registration

Each tool package exports a `TOOL` constant (`ToolDefinition` dataclass with name, description, permissions, run callable). `src.main.discover_tools()` uses `pkgutil.iter_modules()` to find them automatically.

## Dependencies

- `msal` — Azure AD authentication (client credentials + interactive browser)
- `requests` — HTTP client
- `python-dotenv` — .env loading
- `tabulate` — CLI table formatting
- `beautifulsoup4` — HTML parsing (used by standalone PST script)
- `pytest` / `responses` — testing
- `ruff` / `pyright` — linting / type checking

## Standalone Scripts

- `extract_pst_emails.py` — PST email extractor (Windows-only, Outlook COM). Not part of the toolkit menu.

## Documentation

- `docs/implementation-roadmap.md` — Prioritised tool implementation plan (5 tiers)
- `.claude/project-skills/microsoft-admin-knowledge-bank.md` — M365 admin Graph API reference

## Testing

76 tests across:
- `tests/core/` — config, auth (mocked MSAL), graph_client (retry, pagination, errors), utils
- `tests/tools/` — teams_chat_export (messages, media, output formats), enterprise_apps (cert status, SP listing, detail view, delete flow)

## Patterns

- Convention-based tool discovery — add a dir to `src/tools/` with a `TOOL` constant
- Auth per-tool, not per-session — each tool requests minimum scopes
- Delete operations trigger scope upgrade with re-authentication
- Exponential backoff retry for 429/5xx (max 3 retries)
- Auto-fallback from client credentials to delegated on 403 tenant mismatch
- Persistent MSAL token cache (.token_cache.bin) for silent re-auth
- File-lock detection with user prompt loop
- KeyboardInterrupt saves partial data
- `parse_range_selection()` for "1,3,5-8" user input
