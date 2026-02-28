# Enterprise Applications

List, inspect, and manage Azure AD / Entra ID enterprise applications (service principals).

## Permissions

| Type | Scope | When |
|------|-------|------|
| Application | `Application.Read.All` | Listing and viewing details |
| Application | `Application.ReadWrite.All` | Deleting service principals (acquired on demand) |
| Delegated | `Application.Read.All`, `User.Read` | Listing and viewing via browser auth |

## Features

- **List all service principals** with name, creation date, status, certificate expiry, and assignment counts
- **View detailed info** for any app: properties, owners, app roles, users/groups, SSO configuration, and provisioning jobs
- **Delete service principals** with range selection (e.g., `1,3,5-8`) and individual confirmation
- **Certificate monitoring** — shows Valid / Expiring soon (30 days) / Expired status

## User Flow

1. Authenticate and fetch the full list of enterprise applications
2. View as a numbered table with certificate and assignment info
3. Choose: view details, delete apps, or return to main menu
4. Delete operations re-authenticate with `Application.ReadWrite.All` and confirm each deletion individually
