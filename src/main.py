"""Microsoft 365 Admin Toolkit — CLI menu launcher.

Discovers tools automatically from ``src/tools/`` sub-packages that export a
``TOOL`` constant of type :class:`ToolDefinition`.
"""

from __future__ import annotations

import importlib
import pkgutil
import sys

import requests.exceptions

import src.tools as _tools_pkg
from src.core.graph_client import GraphAPIError
from src.tools._base import ToolDefinition


# ---------------------------------------------------------------------------
# Tool discovery
# ---------------------------------------------------------------------------


def discover_tools() -> list[ToolDefinition]:
    """Return all tools found in ``src.tools.*`` sub-packages."""
    tools: list[ToolDefinition] = []
    for module_info in pkgutil.iter_modules(_tools_pkg.__path__, _tools_pkg.__name__ + "."):
        if module_info.name.endswith("._base"):
            continue
        try:
            mod = importlib.import_module(module_info.name)
            tool = getattr(mod, "TOOL", None)
            if isinstance(tool, ToolDefinition):
                tools.append(tool)
        except Exception as exc:
            print(f"  Warning: could not load tool from {module_info.name}: {exc}")
    return tools


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------


def _print_menu(tools: list[ToolDefinition]) -> None:
    print("\n" + "=" * 60)
    print("  Microsoft 365 Admin Toolkit")
    print("=" * 60)
    for idx, tool in enumerate(tools, 1):
        perms_app = ", ".join(tool.permissions_application) or "none"
        perms_del = ", ".join(tool.permissions_delegated) or "none"
        print(f"\n  [{idx}] {tool.name}")
        print(f"      {tool.description}")
        print(f"      App permissions : {perms_app}")
        print(f"      Delegated perms : {perms_del}")
    print("\n  [0] Exit")
    print()


def main() -> None:
    """Entry point: display the tool menu and run the user's selection."""
    tools = discover_tools()
    if not tools:
        print("No tools found. Check that src/tools/ contains valid tool packages.")
        sys.exit(1)

    while True:
        _print_menu(tools)
        try:
            choice = input("Select a tool (number): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not choice:
            continue
        try:
            idx = int(choice)
        except ValueError:
            print("  Invalid input — enter a number.")
            continue

        if idx == 0:
            print("Exiting.")
            break
        if idx < 1 or idx > len(tools):
            print(f"  Invalid choice — enter 1-{len(tools)} or 0 to exit.")
            continue

        tool = tools[idx - 1]
        print(f"\nLaunching: {tool.name}\n{'─' * 40}")
        try:
            tool.run()
        except KeyboardInterrupt:
            print(f"\n\n{tool.name} interrupted.")
        except GraphAPIError as exc:
            print(f"\n  Graph API error: {exc}")
        except requests.exceptions.HTTPError as exc:
            print(f"\n  HTTP error: {exc}")
        except SystemExit:
            pass  # tool may call sys.exit(); don't kill the menu
        print()


if __name__ == "__main__":
    main()
