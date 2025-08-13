"""
Tests for bolt_agent_toolkit.openai module
"""

from unittest.mock import Mock, patch

from bolt_agent_toolkit.configuration import Configuration, Context
from bolt_agent_toolkit.openai.tool import bolt_tool
from bolt_agent_toolkit.openai.toolkit import BoltAgentToolkit


class TestBoltAgentToolkit:
    """Test the BoltAgentToolkit class."""

    def test_toolkit_filters_tools_by_configuration(self, mock_bolt_api):
        """Test that toolkit only includes tools allowed by configuration."""

        # Configuration that only allows product reading
        config = Configuration(
            context=Context(api_key="test", publishable_key="test"),
            actions={"products": {"read": True}, "subscriptions": {"read": False}},
        )

        with patch(
            "bolt_agent_toolkit.openai.toolkit.BoltAPI", return_value=mock_bolt_api
        ):
            toolkit = BoltAgentToolkit(api_key="test", configuration=config)
            tools = toolkit.get_tools()

            # Should only have product-related tools
            tool_names = [tool.name for tool in tools]
            assert all("product" in name.lower() for name in tool_names)

    def test_billing_hook_outcome_type(self, sample_configuration, mock_bolt_api):
        """Test billing hook with outcome-based billing."""
        with patch(
            "bolt_agent_toolkit.openai.toolkit.BoltAPI", return_value=mock_bolt_api
        ):
            toolkit = BoltAgentToolkit(
                api_key="test", configuration=sample_configuration
            )

            billing_hook = toolkit.billing_hook(
                billing_type="outcome", merchant="test_merchant", meter="test_meter"
            )

            assert billing_hook.type == "outcome"
            assert billing_hook.merchant == "test_merchant"
            assert billing_hook.meter == "test_meter"
            assert not billing_hook.meters

    def test_billing_hook_token_type(self, sample_configuration, mock_bolt_api):
        """Test billing hook with token-based billing."""
        with patch(
            "bolt_agent_toolkit.openai.toolkit.BoltAPI", return_value=mock_bolt_api
        ):
            toolkit = BoltAgentToolkit(
                api_key="test", configuration=sample_configuration
            )

            billing_hook = toolkit.billing_hook(
                billing_type="token",
                merchant="test_merchant",
                meters={"input": "input_meter", "output": "output_meter"},
            )

            assert billing_hook.type == "token"
            assert billing_hook.merchant == "test_merchant"
            assert billing_hook.meter is None
            assert billing_hook.meters == {
                "input": "input_meter",
                "output": "output_meter",
            }

    def test_bolt_tool_schema_conversion(self, sample_tool_with_schema):
        """Test that bolt_tool properly converts the schema."""
        # Create a mock BoltAPI
        mock_bolt_api = Mock()

        function_tool = bolt_tool(mock_bolt_api, sample_tool_with_schema)

        # Test that the tool has the correct properties
        assert function_tool.name == "get_product"
        assert function_tool.description == "Get a product by ID"
        assert hasattr(function_tool, "on_invoke_tool")
        assert hasattr(function_tool, "params_json_schema")

        # Test schema conversion
        schema = function_tool.params_json_schema
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert "product_id" in schema["properties"]
        assert schema["properties"]["product_id"]["type"] == "string"
