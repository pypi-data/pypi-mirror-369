#!/usr/bin/env python3
"""
Bolt Agent Toolkit Tools

Unified interface for importing tool modules.
"""

from typing import Any, Callable, Dict, List, TypedDict

from fastmcp.tools.tool import FunctionTool

from ...api import BoltAPI

# Import all tool modules
from .subscription import TOOL_CONFIG as SUBSCRIPTION_TOOL_MAPPINGS
from .subscription import register_tools as register_subscription_tools
from .subscription import set_bolt_api as set_subscription_bolt_api
from .subscription import set_tool_decorator as set_subscription_tool_decorator


class ToolModule(TypedDict):
    """
    TypedDict representing a tool module's interface for the Bolt Agent Toolkit.

    Attributes:
        mappings: A dictionary mapping tool names to their metadata.
        set_client: Function to set the Bolt client for the tool module.
        set_decorator: Function to set the tool decorator for the tool module.
        register_tools: Function to register tools for the tool module.
    """

    mappings: Dict[str, List[Dict[str, Any]]]
    set_client: Callable[[BoltAPI], None]
    set_decorator: Callable[[Callable[..., FunctionTool]], None]
    register_tools: Callable[[List[str]], None]


# Registry of all tool modules
TOOL_MODULES: Dict[str, ToolModule] = {
    "subscription": {
        "mappings": SUBSCRIPTION_TOOL_MAPPINGS,
        "set_client": set_subscription_bolt_api,
        "set_decorator": set_subscription_tool_decorator,
        "register_tools": register_subscription_tools,
    },
}


def get_all_tool_mappings() -> Dict[str, List[Dict[str, Any]]]:
    """Get all tool mappings from all modules."""
    all_mappings: Dict[str, List[Dict[str, Any]]] = {}
    for _, module_data in TOOL_MODULES.items():
        all_mappings.update(module_data["mappings"])
    return all_mappings


def set_bolt_api(api: BoltAPI) -> None:
    """Set the bolt API for all tool modules."""
    for _, module_data in TOOL_MODULES.items():
        module_data["set_client"](api)


def set_tool_decorator(decorator_func: Callable[..., FunctionTool]) -> None:
    """Set the tool decorator for all tool modules."""
    for _, module_data in TOOL_MODULES.items():
        module_data["set_decorator"](decorator_func)


def register_all_tools(tool_names: List[str]) -> None:
    """Register all tools using the decorator approach."""
    for _, module_data in TOOL_MODULES.items():
        module_data["register_tools"](tool_names)
