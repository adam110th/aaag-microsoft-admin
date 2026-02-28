# aaag-microsoft-admin

Microsoft 365 Admin Toolkit — a modular CLI for managing Microsoft 365 resources via the Graph API.

## Tools

| Tool | Description |
|------|-------------|
| **Teams Chat Export** | Export messages and media from a Microsoft Teams chat |
| **Enterprise Applications** | List, inspect, and manage Azure AD service principals (with roles, API permissions, cert status) |

New tools are auto-discovered: add a package to `src/tools/` with a `TOOL` constant and it appears in the menu.

See [`docs/implementation-roadmap.md`](docs/implementation-roadmap.md) for the prioritised plan covering User Management, Group Management, License Management, Security & Compliance tools, and more.

## Prerequisites

- Python 3.14+
- Azure AD app registration with appropriate permissions (each tool lists its own)
- `.env` file with credentials (see [Configuration](#configuration))

## Installation

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root (or copy `.env.example`):

```env
AZURE_TENANT_ID='your-tenant-id'
AZURE_CLIENT_ID='your-client-id'
AZURE_CLIENT_SECRET='your-client-secret'  # optional for delegated auth
```

## Usage

```bash
python -m src
```

This launches the interactive menu showing all available tools with their required permissions. Select a tool by number to run it.

### Architecture

```
src/
  core/           Shared modules (auth, config, Graph client, utilities)
  tools/          Tool packages — each directory is an independent tool
    _base.py      ToolDefinition dataclass
    teams_chat_export/
    enterprise_apps/
  main.py         Menu launcher with auto-discovery
  __main__.py     Entry point for python -m src
```

Each tool declares:
- **Name and description** — shown in the menu
- **Permissions** — application and delegated scopes it requires
- **`run()` function** — entry point called by the menu

Auth is per-tool: each tool requests only the minimum scopes it needs. Delete operations trigger a scope upgrade with re-authentication.

The `GraphClient` supports GET, POST, PATCH, DELETE with automatic retry (429/5xx) and pagination.

## Testing

```bash
pytest tests/
```

## Code Quality

```bash
ruff check .
```

## Standalone Scripts

- `extract_pst_emails.py` — PST email extractor (Windows-only, uses Outlook COM). Not part of the toolkit menu.
