"""Enterprise Applications — manage Azure AD / Entra ID service principals.

Lists all enterprise applications (service principals), shows detailed info
including certificate status, owners, users/groups, SSO, and provisioning.
Supports bulk deletion with individual confirmation.

Permissions:
    Read operations : Application.Read.All (application)
    Delete operations: Application.ReadWrite.All (acquired on demand)
"""

from __future__ import annotations

from datetime import datetime, timezone

from tabulate import tabulate

from requests.exceptions import HTTPError

from src.core.auth import check_token_roles, get_client_credentials_token, get_delegated_token
from src.core.config import GRAPH_BASE, load_environment
from src.core.graph_client import GraphClient, GraphPermissionError
from src.core.utils import parse_range_selection
from src.tools._base import ToolDefinition

# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------

READ_SCOPES_DELEGATED = ["Application.Read.All", "User.Read"]
WRITE_SCOPES_DELEGATED = ["Application.ReadWrite.All", "User.Read"]


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------


def compute_cert_status(
    key_credentials: list[dict],
) -> tuple[str, str]:
    """Compute certificate status from ``keyCredentials``.

    Returns ``(status, expiry_date)`` where status is one of:
    ``"Valid"``, ``"Expiring soon"``, ``"Expired"``, ``"None"``.
    """
    if not key_credentials:
        return ("None", "---")

    now = datetime.now(tz=timezone.utc)
    latest_expiry: datetime | None = None
    latest_expiry_str = "---"

    for cred in key_credentials:
        end_str = cred.get("endDateTime", "")
        if not end_str:
            continue
        try:
            end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        if latest_expiry is None or end_dt > latest_expiry:
            latest_expiry = end_dt
            latest_expiry_str = end_dt.strftime("%Y-%m-%d")

    if latest_expiry is None:
        return ("None", "---")

    days_remaining = (latest_expiry - now).days
    if days_remaining < 0:
        return ("Expired", latest_expiry_str)
    if days_remaining <= 30:
        return ("Expiring soon", latest_expiry_str)
    return ("Valid", latest_expiry_str)


# ---------------------------------------------------------------------------
# Fetch helpers
# ---------------------------------------------------------------------------


def fetch_all_service_principals(client: GraphClient) -> list[dict]:
    """Fetch all service principals with selected fields, handling pagination."""
    select = (
        "id,appId,displayName,createdDateTime,accountEnabled,"
        "keyCredentials,servicePrincipalType"
    )
    url = f"{GRAPH_BASE}/servicePrincipals?$select={select}&$top=100"
    return client.get_paged(url, page_label="service principals")


def fetch_assignments_count(client: GraphClient, sp_id: str) -> int:
    """Return the count of users/groups assigned to a service principal."""
    url = (
        f"{GRAPH_BASE}/servicePrincipals/{sp_id}/appRoleAssignedTo"
        f"?$count=true&$top=1"
    )
    try:
        resp = client.get(url, headers_extra={"ConsistencyLevel": "eventual"})
        return int(resp.json().get("@odata.count", 0))
    except Exception as exc:
        print(f"  WARN: Could not fetch assignment count for {sp_id}: {exc}")
        return 0


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

SORT_LABELS = {
    "name": "Name (A-Z)",
    "created": "Created Date (oldest first)",
    "cert_expiry": "Certificate Expiry (soonest first)",
    "assignments": "Users/Groups (most first)",
}


def sort_apps(apps: list[dict], key: str) -> None:
    """Sort *apps* in-place by *key*.

    Keys:
        ``"name"``         — displayName, case-insensitive, A-Z
        ``"created"``      — createdDateTime, oldest first, missing last
        ``"cert_expiry"``  — soonest certificate expiry first, no-cert last
        ``"assignments"``  — highest assignment count first, unfetched last
    """
    if key == "name":
        apps.sort(key=lambda a: (a.get("displayName") or "").lower())

    elif key == "created":
        def _created_key(a: dict) -> tuple[int, str]:
            val = a.get("createdDateTime", "")
            return (0, val) if val else (1, "")
        apps.sort(key=_created_key)

    elif key == "cert_expiry":
        def _cert_key(a: dict) -> tuple[int, str]:
            _, expiry = compute_cert_status(a.get("keyCredentials", []))
            return (0, expiry) if expiry != "---" else (1, "")
        apps.sort(key=_cert_key)

    elif key == "assignments":
        def _assign_key(a: dict) -> tuple[int, int]:
            val = a.get("_assignments_count", "---")
            if isinstance(val, int):
                # Negate so highest sorts first
                return (0, -val)
            return (1, 0)
        apps.sort(key=_assign_key)


def fetch_all_assignments(client: GraphClient, apps: list[dict]) -> None:
    """Fetch assignment counts for all apps that still show ``"---"``."""
    pending = [a for a in apps if a.get("_assignments_count", "---") == "---"]
    if not pending:
        return
    total = len(pending)
    print(f"  Fetching assignment counts for {total} apps ...")
    for done, app in enumerate(pending, 1):
        app["_assignments_count"] = fetch_assignments_count(client, app["id"])
        if done % 10 == 0 or done == total:
            print(f"    {done}/{total}")


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------


def display_list_table(apps: list[dict]) -> None:
    """Print a numbered table of service principals."""
    rows: list[list] = []
    for idx, app in enumerate(apps, 1):
        cert_status, cert_expiry = compute_cert_status(app.get("keyCredentials", []))
        created = app.get("createdDateTime", "")[:10]
        enabled = "Yes" if app.get("accountEnabled") else "No"
        rows.append([
            idx,
            app.get("displayName", "???")[:50],
            created,
            enabled,
            cert_status,
            cert_expiry,
            app.get("_assignments_count", "---"),
        ])

    headers = ["#", "Name", "Created", "Active", "Cert Status", "Cert Expiry", "Users/Groups"]
    print()
    print(tabulate(rows, headers=headers, tablefmt="simple"))
    print(f"\n  Total: {len(apps)} enterprise applications")


# ---------------------------------------------------------------------------
# Detail view
# ---------------------------------------------------------------------------


def show_app_details(client: GraphClient, app: dict) -> None:
    """Display all detail sections for a single service principal."""
    sp_id = app["id"]
    name = app.get("displayName", "???")
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"{'=' * 60}")

    # 1. Properties
    print("\n--- Properties ---")
    props = [
        ("Display Name", app.get("displayName")),
        ("App ID", app.get("appId")),
        ("Object ID", sp_id),
        ("Type", app.get("servicePrincipalType")),
        ("Created", app.get("createdDateTime")),
        ("Enabled", app.get("accountEnabled")),
    ]
    for label, value in props:
        print(f"  {label:20s}: {value}")

    # 2. Owners
    print("\n--- Owners ---")
    try:
        url = f"{GRAPH_BASE}/servicePrincipals/{sp_id}/owners?$select=displayName,userPrincipalName"
        resp = client.get(url)
        owners = resp.json().get("value", [])
        if owners:
            for owner in owners:
                upn = owner.get("userPrincipalName", "N/A")
                print(f"  {owner.get('displayName', '???')} ({upn})")
        else:
            print("  (none)")
    except Exception as exc:
        print(f"  Error fetching owners: {exc}")

    # 3. Roles and Administrators
    print("\n--- Roles and Administrators ---")

    # 3a. App Roles (roles defined by this application)
    print("\n  App Roles (defined by this application):")
    roles = app.get("appRoles", [])
    if not roles:
        # Fetch full SP to get appRoles if not in original select
        try:
            url = f"{GRAPH_BASE}/servicePrincipals/{sp_id}?$select=appRoles"
            resp = client.get(url)
            roles = resp.json().get("appRoles", [])
        except Exception:
            roles = []

    if roles:
        for role in roles:
            enabled = "enabled" if role.get("isEnabled") else "disabled"
            print(f"    {role.get('displayName', '???')} ({enabled})")
            if role.get("description"):
                print(f"      {role['description'][:80]}")
    else:
        print("    (none)")

    # 3b. Granted API Permissions (what this app is authorized to access)
    print("\n  Granted API Permissions:")
    try:
        url = f"{GRAPH_BASE}/servicePrincipals/{sp_id}/appRoleAssignments"
        resp = client.get(url)
        grants = resp.json().get("value", [])
        if grants:
            for grant in grants:
                resource = grant.get("resourceDisplayName", "???")
                role_id = grant.get("appRoleId", "")
                print(f"    {resource} (role: {role_id[:8]}...)")
        else:
            print("    (none)")
    except Exception as exc:
        print(f"    Error fetching API permissions: {exc}")

    # 4. Users and Groups
    print("\n--- Users and Groups ---")
    try:
        url = f"{GRAPH_BASE}/servicePrincipals/{sp_id}/appRoleAssignedTo?$top=50"
        resp = client.get(url)
        assignments = resp.json().get("value", [])
        if assignments:
            for a in assignments:
                principal = a.get("principalDisplayName", "???")
                ptype = a.get("principalType", "???")
                print(f"  {principal} ({ptype})")
            if len(assignments) == 50:
                print("  ... (more may exist)")
        else:
            print("  (none)")
    except Exception as exc:
        print(f"  Error fetching assignments: {exc}")

    # 5. SSO
    print("\n--- Single Sign-On ---")
    try:
        url = (
            f"{GRAPH_BASE}/servicePrincipals/{sp_id}"
            f"?$select=preferredSingleSignOnMode,samlSingleSignOnSettings"
        )
        resp = client.get(url)
        sso_data = resp.json()
        mode = sso_data.get("preferredSingleSignOnMode", "not configured")
        print(f"  Mode: {mode}")
        saml = sso_data.get("samlSingleSignOnSettings")
        if saml:
            print(f"  SAML relay state: {saml.get('relayState', 'N/A')}")
    except Exception as exc:
        print(f"  Error fetching SSO info: {exc}")

    # 6. Provisioning
    print("\n--- Provisioning ---")
    try:
        url = f"{GRAPH_BASE}/servicePrincipals/{sp_id}/synchronization/jobs"
        resp = client.get(url)
        jobs = resp.json().get("value", [])
        if jobs:
            for job in jobs:
                status = job.get("status", {})
                print(f"  Job: {job.get('templateId', '???')}")
                print(f"    Status: {status.get('code', '???')}")
                last_run = status.get("lastSuccessfulExecutionWithExportedObjects")
                if last_run:
                    print(f"    Last successful run: {last_run}")
        else:
            print("  No provisioning jobs configured")
    except Exception:
        # 404 is expected when synchronization isn't set up
        print("  No provisioning jobs configured")


# ---------------------------------------------------------------------------
# Delete flow
# ---------------------------------------------------------------------------


def delete_apps(
    apps: list[dict],
    env: dict[str, str],
    selected_indices: list[int],
) -> None:
    """Delete selected service principals with individual confirmation."""
    selected = [apps[i - 1] for i in selected_indices]
    print(f"\nYou selected {len(selected)} app(s) for deletion:\n")
    for app in selected:
        print(f"  - {app.get('displayName', '???')} (ID: {app['id']})")

    # Re-authenticate with write permissions if needed
    print("\nDelete requires Application.ReadWrite.All permissions.")
    print("Re-authenticating with elevated scope ...")
    if "AZURE_CLIENT_SECRET" in env:
        token = get_client_credentials_token(env)
    else:
        token = get_delegated_token(env, WRITE_SCOPES_DELEGATED)
    delete_client = GraphClient(token)

    deleted = 0
    skipped = 0
    errors: list[str] = []

    for app in selected:
        name = app.get("displayName", "???")
        sp_id = app["id"]
        try:
            confirm = input(f"\n  Delete '{name}' (ID: {sp_id})? [y/N]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled remaining deletions.")
            break

        if confirm != "y":
            skipped += 1
            print(f"  Skipped '{name}'")
            continue

        try:
            url = f"{GRAPH_BASE}/servicePrincipals/{sp_id}"
            delete_client.delete(url)
            deleted += 1
            print(f"  Deleted '{name}'")
        except Exception as exc:
            errors.append(f"{name}: {exc}")
            print(f"  ERROR deleting '{name}': {exc}")

    print("\n--- Deletion Summary ---")
    print(f"  Deleted : {deleted}")
    print(f"  Skipped : {skipped}")
    if errors:
        print(f"  Errors  : {len(errors)}")
        for err in errors:
            print(f"    {err}")


# ---------------------------------------------------------------------------
# Main run
# ---------------------------------------------------------------------------


def run() -> None:
    """Interactive entry point for Enterprise Applications management."""
    print("Enterprise Applications Manager")
    print("Loading environment ...")
    env = load_environment()

    # Authenticate with read-only permissions
    if "AZURE_CLIENT_SECRET" in env:
        print("Acquiring access token (client credentials) ...")
        token = get_client_credentials_token(env)
    else:
        print("No AZURE_CLIENT_SECRET — using delegated auth ...")
        token = get_delegated_token(env, READ_SCOPES_DELEGATED)

    client = GraphClient(token)
    print("Authenticated successfully.")

    # Warn early if the token is missing required roles
    if "AZURE_CLIENT_SECRET" in env:
        missing = check_token_roles(token, ["Application.Read.All"])
        if missing:
            print(f"\n  WARNING: Token is missing required roles: {', '.join(missing)}")
            print("  The app registration needs these API permissions granted with admin consent.")
            print("  Attempting to proceed anyway ...\n")
        else:
            print()

    # Fetch service principals
    print("Fetching enterprise applications ...")
    try:
        apps = fetch_all_service_principals(client)
    except GraphPermissionError as exc:
        print("\n  ERROR: Insufficient permissions to list enterprise applications.")
        print(f"  Detail: {exc}")
        print()
        print("  To fix this, add the following to your Azure AD app registration:")
        print("    1. Go to Azure Portal > App registrations > your app")
        print("    2. API permissions > Add a permission > Microsoft Graph")
        print("    3. Application permissions > Application.Read.All")
        print("    4. Click 'Grant admin consent' (requires Global Administrator)")
        print()
        print("  Current token roles can be viewed in the diagnostic output above.")
        return
    except HTTPError as exc:
        print(f"\n  ERROR: Failed to fetch enterprise applications: {exc}")
        return

    if not apps:
        print("No enterprise applications found.")
        return

    # Enrich with assignment counts (first 20 only to avoid throttling)
    print("Fetching assignment counts ...")
    for app in apps[:20]:
        app["_assignments_count"] = fetch_assignments_count(client, app["id"])

    # Default sort by name
    current_sort = "name"
    sort_apps(apps, current_sort)
    display_list_table(apps)

    # Sub-menu loop
    while True:
        print(f"\n  Current sort: {SORT_LABELS.get(current_sort, current_sort)}")
        print("\n  [1] View app details")
        print("  [2] Delete apps")
        print("  [3] Sort list")
        print("  [0] Return to main menu")
        try:
            choice = input("\nChoice: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if choice == "0" or not choice:
            break

        if choice == "1":
            try:
                num = input(f"  Enter app number (1-{len(apps)}): ").strip()
            except (KeyboardInterrupt, EOFError):
                print()
                continue
            try:
                idx = int(num)
                if idx < 1 or idx > len(apps):
                    print(f"  Invalid — enter 1-{len(apps)}")
                    continue
            except ValueError:
                print("  Invalid number.")
                continue
            show_app_details(client, apps[idx - 1])

        elif choice == "2":
            try:
                range_input = input(
                    f"  Enter app numbers to delete (e.g. 1,3,5-8) [1-{len(apps)}]: "
                ).strip()
            except (KeyboardInterrupt, EOFError):
                print()
                continue
            if not range_input:
                continue
            selected = parse_range_selection(range_input, len(apps))
            if not selected:
                print("  No valid selections.")
                continue
            delete_apps(apps, env, selected)
            # Refresh the list after deletions
            print("\nRefreshing list ...")
            try:
                apps = fetch_all_service_principals(client)
            except (GraphPermissionError, HTTPError) as exc:
                print(f"  ERROR refreshing list: {exc}")
                break
            if not apps:
                print("No enterprise applications remaining.")
                break
            # Re-apply sort after refresh
            if current_sort == "assignments":
                fetch_all_assignments(client, apps)
            sort_apps(apps, current_sort)
            display_list_table(apps)

        elif choice == "3":
            print("\n  Sort by:")
            print("    [1] Name (A-Z)")
            print("    [2] Created Date (oldest first)")
            print("    [3] Certificate Expiry (soonest first)")
            print("    [4] Users/Groups (most first)")
            print("    [0] Cancel")
            try:
                sort_choice = input("\n  Sort choice: ").strip()
            except (KeyboardInterrupt, EOFError):
                print()
                continue
            sort_map = {"1": "name", "2": "created", "3": "cert_expiry", "4": "assignments"}
            new_sort = sort_map.get(sort_choice)
            if not new_sort:
                if sort_choice != "0":
                    print("  Invalid sort choice.")
                continue
            if new_sort == "assignments":
                fetch_all_assignments(client, apps)
            current_sort = new_sort
            sort_apps(apps, current_sort)
            display_list_table(apps)

        else:
            print("  Invalid choice.")


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------

TOOL = ToolDefinition(
    name="Enterprise Applications",
    description="List, inspect, and manage Azure AD enterprise applications (service principals).",
    permissions_application=["Application.Read.All"],
    permissions_delegated=["Application.Read.All", "User.Read"],
    run=run,
)
