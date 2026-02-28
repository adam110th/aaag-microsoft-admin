# Enterprise Applications

List, inspect, and manage Azure AD / Entra ID enterprise applications (service principals).

## Permissions

| Type | Scope | When | Admin Consent |
|------|-------|------|---------------|
| Application | `Application.Read.All` | Listing and viewing details | Required |
| Application | `Application.ReadWrite.All` | Deleting service principals (acquired on demand) | Required |
| Delegated | `Application.Read.All`, `User.Read` | Listing and viewing via browser auth | Required |
| Delegated | `Application.ReadWrite.All`, `User.Read` | Deleting via browser auth | Required |

### Setting Up Permissions

1. Go to **Azure Portal** > **App registrations** > select your app
2. **API permissions** > **Add a permission** > **Microsoft Graph**
3. Choose **Application permissions** (for client credentials) or **Delegated permissions** (for browser auth)
4. Search for and add `Application.Read.All`
5. Click **Grant admin consent for [your tenant]** (requires Global Administrator or Privileged Role Administrator)

### Verifying Permissions

When the tool authenticates, it displays the token's granted roles. If `Application.Read.All` is not listed, the tool will fail with a `403 Insufficient privileges` error and display instructions to fix it.

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `HTTP 403: Authorization_RequestDenied` | Missing `Application.Read.All` permission | Add the permission and grant admin consent (see above) |
| `Insufficient privileges to complete the operation` | Permission added but admin consent not granted | Click "Grant admin consent" in Azure Portal |
| Token roles show only Chat-related permissions | App has Chat permissions but not Application permissions | Add `Application.Read.All` to the same app registration |

## Features

- **List all service principals** with name, creation date, status, certificate expiry, and assignment counts
- **Sort by** Name (default), Created Date, Certificate Expiry, or Users/Groups — sort persists after delete+refresh
- **View detailed info** for any app: properties, owners, app roles, granted API permissions, users/groups, SSO configuration, and provisioning jobs
- **Delete service principals** with range selection (e.g., `1,3,5-8`) and individual confirmation
- **Certificate monitoring** — shows Valid / Expiring soon (30 days) / Expired status

## User Flow

1. Authenticate and validate token permissions
2. Fetch the full list of enterprise applications
3. View as a numbered table with certificate and assignment info
4. Choose: view details, sort list, delete apps, or return to main menu
5. Delete operations re-authenticate with `Application.ReadWrite.All` and confirm each deletion individually
