# Teams Chat Export

Export Microsoft Teams chat conversations — including messages, images, and file attachments — using the Microsoft Graph API.

## Permissions

| Type | Scope | When |
|------|-------|------|
| Application | `Chat.Read.All` | Same-tenant chats (admin-consented) |
| Delegated | `Chat.Read`, `Chat.ReadBasic`, `User.Read` | Cross-tenant/federated chats |

## Authentication Modes

| Mode | When to use |
|------|-------------|
| Client credentials (default) | Same-tenant chats where `Chat.Read.All` is granted |
| Delegated (browser sign-in) | Cross-tenant/federated chats (e.g., external guests) |

If client credentials fail with a `403 Tenant Id mismatch` error, the tool automatically falls back to delegated auth. The delegated flow caches tokens in `.token_cache.bin` for subsequent runs.

## Output

Each export creates a timestamped directory under `exports/`:

```
exports/{chat_id}_{timestamp}/
  messages.json          Full message data with local media paths
  messages.md            Markdown conversation log
  messages.csv           Flattened CSV for Excel review
  export_metadata.json   Run stats and error log
  media/                 Downloaded images and attachments
```
