"""Base definitions for toolkit tools."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolDefinition:
    """Metadata for a single tool in the Microsoft 365 Admin toolkit."""

    name: str
    description: str
    permissions_application: list[str]
    permissions_delegated: list[str]
    run: Callable[[], None]
