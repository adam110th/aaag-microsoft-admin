# Implementation Roadmap — aaag-microsoft-admin

Prioritised tool implementation plan for the Microsoft 365 Admin Toolkit.

> Each tier is ordered by daily admin impact. Implement tools top-down within each tier.

---

## Current Tools (implemented)

| Tool | Status | Description |
|------|--------|-------------|
| Teams Chat Export | Done | Export messages and media from a Microsoft Teams chat |
| Enterprise Applications | Done | List, inspect, delete Azure AD service principals (with roles, permissions, cert status) |

---

## Tier 1 — Daily Admin Tasks (implement next)

| Tool | Description | Key Permissions |
|------|-------------|-----------------|
| **User Management** | List/search/create/disable users, reset passwords, manage licenses | `User.ReadWrite.All`, `UserAuthenticationMethod.ReadWrite.All` |
| **Group Management** | List/search groups, manage members, create/delete | `Group.ReadWrite.All`, `GroupMember.ReadWrite.All` |
| **License Management** | View SKU inventory, usage counts, assign/remove per user | `Organization.Read.All`, `User.ReadWrite.All` |

### User Management — Feature Details
- List all users with key properties (display name, UPN, enabled, last sign-in)
- Search by name, email, or department
- Create new user with required fields
- Disable/enable user account
- Reset password (generate temporary)
- Assign/remove licenses
- View sign-in activity

### Group Management — Feature Details
- List all groups with type (Security, M365, Distribution)
- Search by name
- View group members
- Add/remove members
- Create new group (security or M365)
- Delete group with confirmation

### License Management — Feature Details
- Display all subscribed SKUs with total/assigned/available counts
- Show per-user license assignments
- Assign license to user
- Remove license from user
- Export license report to CSV/Excel

---

## Tier 2 — Security & Compliance

| Tool | Description | Key Permissions |
|------|-------------|-----------------|
| **Conditional Access Policies** | List/view/export/create CA policies | `Policy.Read.All`, `Policy.ReadWrite.ConditionalAccess` |
| **Sign-in & Audit Logs** | Query sign-in logs, filter by user/app/status, export | `AuditLog.Read.All` |
| **Security Score Dashboard** | Display secure score, list improvement actions | `SecurityEvents.Read.All` |

### Conditional Access — Feature Details
- List all CA policies with state (enabled/disabled/report-only)
- Detail view: conditions, grant controls, session controls
- Export all policies as JSON (backup)
- Create new policy from template
- Toggle policy state

### Sign-in & Audit Logs — Feature Details
- Query sign-in logs with filters (user, app, date range, status)
- Show failed sign-ins with failure reasons
- Query directory audit logs
- Export results to CSV
- Summary statistics (success rate, top failures)

### Security Score Dashboard — Feature Details
- Display current secure score and max score
- List control profiles with current/max scores
- Show recommended improvement actions
- Filter by category (Identity, Data, Device, Apps)

---

## Tier 3 — Infrastructure Management

| Tool | Description | Key Permissions |
|------|-------------|-----------------|
| **SharePoint Site Manager** | List sites, view storage usage, manage permissions | `Sites.ReadWrite.All` |
| **Teams Manager** | List/archive teams, view members and channels | `Team.ReadBasic.All`, `Group.ReadWrite.All` |
| **App Registration Manager** | Manage app registrations, track secret/cert expiry | `Application.ReadWrite.All` |

### SharePoint Site Manager — Feature Details
- List all sites with storage used/quota
- Search sites by name or URL
- View site permissions
- View document libraries
- Storage usage report

### Teams Manager — Feature Details
- List all teams with member counts
- View team details (channels, members, settings)
- Archive/unarchive teams
- Add/remove team members
- List teams with no activity (cleanup candidates)

### App Registration Manager — Feature Details
- List all app registrations
- Show secret/certificate expiry dates
- Alert on expiring credentials (30/60/90 day warnings)
- Add new client secret
- Remove expired secrets
- Export credential expiry report

---

## Tier 4 — Device & Endpoint Management

| Tool | Description | Key Permissions |
|------|-------------|-----------------|
| **Intune Device Inventory** | List devices, compliance status, OS versions | `DeviceManagementManagedDevices.Read.All` |
| **Intune Compliance Reporter** | Compliance policies, non-compliant device counts | `DeviceManagementConfiguration.Read.All` |

### Intune Device Inventory — Feature Details
- List all managed devices with OS, compliance, last check-in
- Filter by OS, compliance status, ownership type
- View device details
- Export device inventory to CSV/Excel
- Summary: device count by OS, compliance breakdown

### Intune Compliance Reporter — Feature Details
- List compliance policies with device state summaries
- Show non-compliant devices per policy
- Overall compliance percentage
- Export compliance report

---

## Tier 5 — Advanced / Specialized

| Tool | Description | Key Permissions |
|------|-------------|-----------------|
| **Usage Reports Exporter** | Pull M365 usage reports, export CSV/Excel | `Reports.Read.All` |
| **Directory Role Auditor** | List privileged role assignments, detect over-privileged accounts | `RoleManagement.Read.Directory` |
| **Named Locations Manager** | Manage IP ranges and countries for CA policies | `Policy.Read.All`, `Policy.ReadWrite.ConditionalAccess` |
| **Administrative Unit Manager** | Scoped administration for large organisations | `AdministrativeUnit.ReadWrite.All` |
| **eDiscovery Case Manager** | Legal/compliance case management | `eDiscovery.Read.All` |

---

## Implementation Notes

### Adding a New Tool

1. Create a new package directory under `src/tools/` (e.g., `src/tools/user_management/`)
2. Create `tool.py` with a `run()` function and a `TOOL` constant (`ToolDefinition`)
3. The tool auto-appears in the menu via `pkgutil` discovery
4. Add tests in `tests/tools/`

### Shared Infrastructure Available

- `GraphClient` — GET/POST/PATCH/DELETE with retry and pagination
- `load_environment()` — .env loading with required/optional variable validation
- `get_client_credentials_token()` / `get_delegated_token()` — MSAL auth
- `write_with_lock_check()` — file writing with lock detection
- `parse_range_selection()` — "1,3,5-8" user input parsing
- `GRAPH_BASE` / `GRAPH_BETA` — API base URL constants

### Permission Strategy

- Each tool requests only the minimum scopes it needs
- Read-only operations use `*.Read.All` permissions
- Write operations trigger scope upgrade with re-authentication
- Client credentials flow for automation; delegated flow for interactive use
