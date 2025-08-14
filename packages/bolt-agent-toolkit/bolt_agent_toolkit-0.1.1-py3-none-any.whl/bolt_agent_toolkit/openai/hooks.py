"""OpenAI agent hooks for Bolt Agent Toolkit.

This module defines hooks for integrating Bolt API metering and billing
with OpenAI-based agent runs.
"""

from typing import Any, Dict, Optional

from agents import Agent, AgentHooks, RunContextWrapper

from ..api import BoltAPI


class BillingHooks(AgentHooks):
    """
    AgentHooks implementation for handling Bolt API metering and billing events.

    This class provides hooks to record metering events (such as outcome or token usage)
    for OpenAI-based agent runs, integrating with the BoltAPI for billing purposes.
    """

    bolt: BoltAPI

    def __init__(
        self,
        billing_type: str,
        merchant: str,
        meter: Optional[str] = None,
        meters: Optional[Dict[str, str]] = None,
    ):
        self.type = billing_type
        self.merchant = merchant
        self.meter = meter
        self.meters = meters if meters else {}

    def set_bolt_api(self, bolt: BoltAPI) -> None:
        """
        Set the BoltAPI instance to be used for metering and billing events.

        Args:
            bolt (BoltAPI): The BoltAPI instance to use.
        """
        self.bolt = bolt

    async def on_end(
        self,
        context: RunContextWrapper,
        _: Agent,
        __: Any,
    ) -> None:
        if self.type == "outcome" and self.meter is not None:
            self.bolt.create_meter_event(self.meter, self.merchant)

        if self.type == "token":
            if self.meters["input"]:
                self.bolt.create_meter_event(
                    self.meters["input"],
                    self.merchant,
                    str(context.usage.input_tokens),
                )
            if self.meters["output"]:
                self.bolt.create_meter_event(
                    self.meters["output"],
                    self.merchant,
                    str(context.usage.output_tokens),
                )
