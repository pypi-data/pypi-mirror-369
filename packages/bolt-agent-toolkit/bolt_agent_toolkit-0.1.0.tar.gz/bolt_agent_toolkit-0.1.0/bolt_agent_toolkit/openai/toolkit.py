"""Bolt Agent Toolkit."""

from typing import List, Optional

from agents import FunctionTool

from ..api import BoltAPI
from ..configuration import Configuration, is_tool_allowed
from ..tools import tools
from .hooks import BillingHooks
from .tool import bolt_tool


class BoltAgentToolkit:
    """
    Toolkit for integrating Bolt API with OpenAI-based agent runs.

    This class provides a collection of tools and hooks for
    interacting with the Bolt API from OpenAI-based agents.
    It allows agents to perform various operations using Bolt API
    methods, including product management, subscription handling, and metering.
    """

    def __init__(self, api_key: str, configuration: Configuration):
        context = configuration.get("context") if configuration else None

        self._bolt_api: BoltAPI = BoltAPI(api_key=api_key, context=context)

        filtered_tools = [
            tool for tool in tools if is_tool_allowed(tool, configuration)
        ]

        self._tools: List[FunctionTool] = [
            bolt_tool(self._bolt_api, tool) for tool in filtered_tools
        ]

    def get_tools(self) -> List[FunctionTool]:
        """Get the tools in the toolkit."""
        return self._tools

    def billing_hook(
        self,
        billing_type: str,
        merchant: str,
        meter: Optional[str] = None,
        meters: Optional[dict[str, str]] = None,
    ) -> BillingHooks:
        """
        Create a BillingHooks instance for metering and billing events.

        Args:
            billing_type (Optional[str]): The type of billing event.
            merchant (Optional[str]): The merchant identifier for billing.
            meter (Optional[str]): The meter identifier for outcome-based billing.
            meters (Optional[dict[str, str]]): A dictionary of meter identifiers
                                                for token-based billing.

        Returns:
            BillingHooks: An instance of BillingHooks configured for the
                         specified billing type.
        """
        hook = BillingHooks(billing_type, merchant, meter, meters)
        hook.set_bolt_api(self._bolt_api)
        return hook
