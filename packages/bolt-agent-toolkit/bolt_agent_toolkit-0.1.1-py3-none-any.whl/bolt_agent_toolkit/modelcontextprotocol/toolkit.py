"""
Bolt Agent Toolkit MCP Implementation
"""

import tomllib
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from fastmcp import FastMCP

from ..api import BoltAPI
from ..configuration import Actions, Configuration
from ..tools import tools as all_tools

# Import tools from the modelcontextprotocol/src/tools folder
from .tools import (
    get_all_tool_mappings,
    register_all_tools,
    set_bolt_api,
    set_tool_decorator,
)

# Define accepted tools
ACCEPTED_TOOLS = [
    "products.read",
    "products.create",
    "subscriptions.read",
    "subscriptions.update",
    "subscriptions.delete",
    "plans.read",
]


def get_version_from_pyproject() -> str:
    """Get version from pyproject.toml in the parent directory."""
    try:
        # Navigate to the python directory (parent of bolt_agent_toolkit)
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return cast(str, data["project"]["version"])
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        return "0.1.0"  # Fallback version


class BoltAgentToolkit(FastMCP):
    """Bolt Agent Toolkit MCP Server implementation."""

    def __init__(
        self,
        api_key: str,
        tools: List[str],
        configuration: Optional[Configuration] = None,
    ):
        super().__init__(
            name="Bolt",
            version=get_version_from_pyproject(),
        )

        self.api_key = api_key
        self.tools = tools
        self.configuration = configuration or Configuration()

        # Have all tools available in configuration
        actions: Dict[str, Any] = {}
        for tool in all_tools:
            for resource, _actions in tool.actions.items():
                # actions = cast(Actions, actions)
                if resource not in actions:
                    actions[resource] = _actions
                else:
                    actions[resource].update(_actions)

        self.configuration["actions"] = cast(Actions, actions)

        # Initialize Bolt API
        self.bolt_api = BoltAPI(
            api_key=api_key, context=self.configuration.get("context")
        )

        # Set the bolt API and tool decorator for all tools
        set_bolt_api(self.bolt_api)
        set_tool_decorator(self.tool)

        # Register tools
        self._register_tools()

    def _register_tools(self) -> None:
        """Register only those tools that are enabled in configuration."""
        # Get all available tool mappings
        all_tool_mappings = get_all_tool_mappings()

        # Determine which tools to register
        tools_to_register = []
        for tool_name in self.tools:
            if tool_name == "all":
                # Register all tools
                tools_to_register = list(all_tool_mappings.keys())
                break

            if tool_name in all_tool_mappings:
                if self._is_tool_allowed(tool_name):
                    tools_to_register.append(tool_name)

        register_all_tools(tools_to_register)

    def _is_tool_allowed(self, tool_name: str) -> bool:
        """Check if a tool is allowed based on configuration."""
        resource, action = tool_name.split(".")
        return bool(
            isinstance(self.configuration.get("actions", {}), dict)
            and self.configuration.get("actions", {})  # type: ignore
            .get(resource, {})
            .get(action, False)
        )
