"""Bolt Agent Toolkit for LangChain."""

from typing import List

from ..api import BoltAPI
from ..configuration import Configuration, is_tool_allowed
from ..tools import tools
from .tool import BoltTool


class BoltAgentToolkit:
    """Bolt Agent Toolkit for LangChain integration."""

    def __init__(
        self,
        api_key: str,
        configuration: Configuration,
    ):
        context = configuration.get("context") if configuration else None

        self._bolt_api = BoltAPI(api_key=api_key, context=context)

        filtered_tools = [
            tool for tool in tools if is_tool_allowed(tool, configuration)
        ]

        self._tools: List[BoltTool] = [
            BoltTool(
                name=tool.method,
                description=tool.description,
                method=tool.method,
                bolt_api=self._bolt_api,
                args_schema=tool.args_schema,
            )
            for tool in filtered_tools
        ]

    def get_api(self) -> BoltAPI:
        """Get the Bolt API instance."""
        return self._bolt_api

    def get_tools(self) -> List[BoltTool]:
        """Get the tools in the toolkit."""
        return self._tools
