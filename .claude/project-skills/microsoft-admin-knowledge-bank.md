# Microsoft 365 Admin Knowledge Bank

> Project skill for aaag-microsoft-admin. This reference documents Microsoft 365 admin capabilities available via Microsoft Graph API, organised by service area. Use this to suggest and implement new admin tools.

---

## Entra ID (Azure AD)

### Users
| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /users` | `User.Read.All` | List all users |
| `GET /users/{id}` | `User.Read.All` | Get user details |
| `POST /users` | `User.ReadWrite.All` | Create user |
| `PATCH /users/{id}` | `User.ReadWrite.All` | Update user properties |
| `DELETE /users/{id}` | `User.ReadWrite.All` | Delete user |
| `POST /users/{id}/assignLicense` | `User.ReadWrite.All` | Assign/remove licenses |
| `POST /users/{id}/authentication/methods/{id}/resetPassword` | `UserAuthenticationMethod.ReadWrite.All` | Reset password |
| `PATCH /users/{id} (accountEnabled)` | `User.ReadWrite.All` | Enable/disable user |

### Groups
| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /groups` | `Group.Read.All` | List all groups |
| `GET /groups/{id}` | `Group.Read.All` | Get group details |
| `POST /groups` | `Group.ReadWrite.All` | Create group |
| `DELETE /groups/{id}` | `Group.ReadWrite.All` | Delete group |
| `GET /groups/{id}/members` | `GroupMember.Read.All` | List group members |
| `POST /groups/{id}/members/$ref` | `GroupMember.ReadWrite.All` | Add member |
| `DELETE /groups/{id}/members/{id}/$ref` | `GroupMember.ReadWrite.All` | Remove member |

### App Registrations
| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /applications` | `Application.Read.All` | List all app registrations |
| `GET /applications/{id}` | `Application.Read.All` | Get app registration details |
| `POST /applications` | `Application.ReadWrite.All` | Create app registration |
| `PATCH /applications/{id}` | `Application.ReadWrite.All` | Update app registration |
| `DELETE /applications/{id}` | `Application.ReadWrite.All` | Delete app registration |
| `POST /applications/{id}/addPassword` | `Application.ReadWrite.All` | Add client secret |
| `POST /applications/{id}/removePassword` | `Application.ReadWrite.All` | Remove client secret |

### Enterprise Applications (Service Principals)
| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /servicePrincipals` | `Application.Read.All` | List all enterprise apps |
| `GET /servicePrincipals/{id}` | `Application.Read.All` | Get enterprise app details |
| `DELETE /servicePrincipals/{id}` | `Application.ReadWrite.All` | Delete enterprise app |
| `GET /servicePrincipals/{id}/appRoleAssignedTo` | `Application.Read.All` | Users/groups assigned |
| `GET /servicePrincipals/{id}/appRoleAssignments` | `Application.Read.All` | API permissions granted |
| `GET /servicePrincipals/{id}/owners` | `Application.Read.All` | List owners |

### Conditional Access
| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /identity/conditionalAccess/policies` | `Policy.Read.All` | List CA policies |
| `GET /identity/conditionalAccess/policies/{id}` | `Policy.Read.All` | Get policy details |
| `POST /identity/conditionalAccess/policies` | `Policy.ReadWrite.ConditionalAccess` | Create CA policy |
| `PATCH /identity/conditionalAccess/policies/{id}` | `Policy.ReadWrite.ConditionalAccess` | Update CA policy |
| `DELETE /identity/conditionalAccess/policies/{id}` | `Policy.ReadWrite.ConditionalAccess` | Delete CA policy |
| `GET /identity/conditionalAccess/namedLocations` | `Policy.Read.All` | List named locations |

### Directory Roles
| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /directoryRoles` | `RoleManagement.Read.Directory` | List activated directory roles |
| `GET /directoryRoles/{id}/members` | `RoleManagement.Read.Directory` | List role members |
| `GET /roleManagement/directory/roleAssignments` | `RoleManagement.Read.Directory` | List all role assignments |

### Audit & Sign-in Logs
| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /auditLogs/directoryAudits` | `AuditLog.Read.All` | Directory audit logs |
| `GET /auditLogs/signIns` | `AuditLog.Read.All` | Sign-in logs |
| `GET /auditLogs/provisioning` | `AuditLog.Read.All` | Provisioning logs |

### Identity Protection
| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /identityProtection/riskyUsers` | `IdentityRiskyUser.Read.All` | List risky users |
| `GET /identityProtection/riskDetections` | `IdentityRiskEvent.Read.All` | Risk detection events |

---

## Microsoft 365 Licensing

| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /subscribedSkus` | `Organization.Read.All` | List all license SKUs with counts |
| `GET /users/{id}/licenseDetails` | `User.Read.All` | User's assigned licenses |
| `POST /users/{id}/assignLicense` | `User.ReadWrite.All` | Assign/remove licenses |
| `GET /reports/getOffice365ActiveUserDetail` | `Reports.Read.All` | Active user license usage |

---

## Exchange Online

| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /users/{id}/mailboxSettings` | `MailboxSettings.Read` | Mailbox settings (auto-reply, timezone) |
| `PATCH /users/{id}/mailboxSettings` | `MailboxSettings.ReadWrite` | Update mailbox settings |
| `GET /users/{id}/mailFolders` | `Mail.Read` | List mail folders |
| `GET /groups?$filter=groupTypes/any(c:c eq 'Unified')` | `Group.Read.All` | Distribution lists / M365 groups |
| `GET /users/{id}/messages` | `Mail.Read` | List messages |

---

## SharePoint Online

| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /sites` | `Sites.Read.All` | Search/list sites |
| `GET /sites/{id}` | `Sites.Read.All` | Get site details |
| `GET /sites/{id}/drives` | `Sites.Read.All` | List document libraries |
| `GET /sites/{id}/permissions` | `Sites.FullControl.All` | Site permissions |
| `GET /sites/{id}/lists` | `Sites.Read.All` | List SharePoint lists |
| `GET /admin/sharepoint/settings` (beta) | `SharePointTenantSettings.Read.All` | Tenant SharePoint settings |

---

## Microsoft Teams

| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /teams` | `Team.ReadBasic.All` | List all teams |
| `GET /teams/{id}` | `Team.ReadBasic.All` | Get team details |
| `GET /teams/{id}/channels` | `Channel.ReadBasic.All` | List channels |
| `GET /teams/{id}/members` | `TeamMember.Read.All` | List team members |
| `POST /teams/{id}/members` | `TeamMember.ReadWrite.All` | Add member |
| `POST /teams/{id}/archive` | `TeamSettings.ReadWrite.All` | Archive team |
| `GET /chats` | `Chat.Read.All` | List chats |
| `GET /chats/{id}/messages` | `Chat.Read.All` | Read chat messages |

---

## Intune / Endpoint Management

### Managed Devices
| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /deviceManagement/managedDevices` | `DeviceManagementManagedDevices.Read.All` | List managed devices |
| `GET /deviceManagement/managedDevices/{id}` | `DeviceManagementManagedDevices.Read.All` | Device details |
| `POST /deviceManagement/managedDevices/{id}/wipe` | `DeviceManagementManagedDevices.PrivilegedOperations.All` | Wipe device |
| `POST /deviceManagement/managedDevices/{id}/retire` | `DeviceManagementManagedDevices.PrivilegedOperations.All` | Retire device |

### Compliance
| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /deviceManagement/deviceCompliancePolicies` | `DeviceManagementConfiguration.Read.All` | List compliance policies |
| `GET /deviceManagement/deviceCompliancePolicyDeviceStateSummary` | `DeviceManagementConfiguration.Read.All` | Compliance summary |

### Configuration
| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /deviceManagement/deviceConfigurations` | `DeviceManagementConfiguration.Read.All` | List device config profiles |
| `GET /deviceManagement/deviceEnrollmentConfigurations` | `DeviceManagementServiceConfig.Read.All` | Enrollment configs |

### Apps
| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /deviceAppManagement/mobileApps` | `DeviceManagementApps.Read.All` | List managed apps |
| `GET /deviceAppManagement/mobileAppConfigurations` | `DeviceManagementApps.Read.All` | App config policies |

---

## Security & Compliance

| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /security/alerts_v2` | `SecurityAlert.Read.All` | Security alerts |
| `GET /security/secureScores` | `SecurityEvents.Read.All` | Secure score history |
| `GET /security/secureScoreControlProfiles` | `SecurityEvents.Read.All` | Improvement actions |
| `GET /security/incidents` | `SecurityIncident.Read.All` | Security incidents |
| `GET /security/cases/ediscoveryCases` (beta) | `eDiscovery.Read.All` | eDiscovery cases |

---

## Reports & Analytics

| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /reports/getOffice365ActiveUserCounts` | `Reports.Read.All` | Active user counts |
| `GET /reports/getOffice365ActiveUserDetail` | `Reports.Read.All` | Per-user activity detail |
| `GET /reports/getMailboxUsageDetail` | `Reports.Read.All` | Mailbox storage usage |
| `GET /reports/getSharePointSiteUsageDetail` | `Reports.Read.All` | SharePoint site usage |
| `GET /reports/getTeamsUserActivityUserDetail` | `Reports.Read.All` | Teams user activity |
| `GET /reports/getOneDriveUsageAccountDetail` | `Reports.Read.All` | OneDrive usage |
| `GET /reports/getEmailActivityUserDetail` | `Reports.Read.All` | Email activity |
| `GET /reports/credentialUserRegistrationDetails` | `Reports.Read.All` | MFA registration status |

---

## Administrative Units

| Endpoint | Permission | Description |
|----------|------------|-------------|
| `GET /directory/administrativeUnits` | `AdministrativeUnit.Read.All` | List admin units |
| `POST /directory/administrativeUnits` | `AdministrativeUnit.ReadWrite.All` | Create admin unit |
| `GET /directory/administrativeUnits/{id}/members` | `AdministrativeUnit.Read.All` | List members |

---

## Notes

- All endpoints use the `https://graph.microsoft.com/v1.0` base URL unless marked as (beta).
- Beta endpoints use `https://graph.microsoft.com/beta`.
- Permissions listed are **application** permissions. Delegated permissions may differ.
- The existing codebase uses `GRAPH_BASE` and `GRAPH_BETA` constants from `src/core/config.py`.
- See `docs/implementation-roadmap.md` for the prioritised build order.
