"""Configuration types and utilities for Bolt Agent Toolkit."""

from typing import Optional

from typing_extensions import TypedDict

from .schema import Tool


# Define Permission type
class Permission(TypedDict, total=False):
    """Permission configuration for CRUD operations."""

    create: Optional[bool]
    update: Optional[bool]
    read: Optional[bool]
    delete: Optional[bool]


# Define Actions type
class Actions(TypedDict, total=False):
    """Actions configuration for different resources."""

    products: Optional[Permission]
    subscriptions: Optional[Permission]
    plans: Optional[Permission]
    orders: Optional[Permission]


# Define Context type
class Context(TypedDict, total=False):
    """Context configuration for API settings."""

    api_key: Optional[str]
    publishable_key: Optional[str]
    base_url: Optional[str]
    timeout: Optional[float]
    environment: Optional[str]


# Define Configuration type
class Configuration(TypedDict, total=False):
    """Main configuration for Bolt Agent Toolkit."""

    actions: Optional[Actions]
    context: Optional[Context]


def is_tool_allowed(tool: Tool, configuration: Configuration) -> bool:
    """Check if a tool is allowed based on configuration."""
    actions_config = configuration.get("actions") or {}
    # if there are no actions configured, nothing is allowed
    if not actions_config:
        return False

    for resource, required_perms in tool.actions.items():
        # must have that resource in your config
        resource_perms = actions_config.get(resource)
        if not resource_perms:
            return False

        # for each permission the tool needs, config must allow it
        for perm in required_perms:
            if not resource_perms.get(perm, False):  # type: ignore[attr-defined]
                return False

    return True
