"""
This tool allows agents to interact with the Bolt API.
"""

from __future__ import annotations

import json
from typing import Any

from agents import FunctionTool
from agents.run_context import RunContextWrapper

from ..api import BoltAPI
from ..schema import Tool


def bolt_tool(api: BoltAPI, tool: Tool) -> FunctionTool:
    """
    Create a FunctionTool for interacting with the Bolt API.

    This function constructs a FunctionTool that wraps a Bolt API method,
    allowing agents to invoke Bolt API operations through OpenAI.
    """

    async def on_invoke_tool(
        _: RunContextWrapper[Any],
        input_str: str,
    ) -> str:
        method = getattr(api, tool.method)
        args = json.loads(input_str)
        value = method(**args)
        assert isinstance(value, str)
        return value

    parameters = tool.args_schema.model_json_schema()
    parameters["additionalProperties"] = False
    parameters["type"] = "object"

    # Remove the description field from parameters as it's
    # not needed in the OpenAI function schema
    if "description" in parameters:
        del parameters["description"]

    if "title" in parameters:
        del parameters["title"]

    # Remove title and default fields from properties
    if "properties" in parameters:
        for prop in parameters["properties"].values():
            if "title" in prop:
                del prop["title"]
            if "default" in prop:
                del prop["default"]

    return FunctionTool(
        name=tool.method,
        description=tool.description,
        params_json_schema=parameters,
        on_invoke_tool=on_invoke_tool,
        strict_json_schema=False,
    )
