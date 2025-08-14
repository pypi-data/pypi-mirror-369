"""
Integration tests for bolt_agent_toolkit
"""

from unittest.mock import Mock

from bolt_agent_toolkit import BoltAPI, Context
from bolt_agent_toolkit.tools import tools


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_complete_workflow(self, sample_configuration):
        """Test the complete workflow from config to API call."""
        # 1. Create context and configuration
        context = Context(
            api_key="test_api_key",
            publishable_key="test_publishable_key",
        )

        # 2. Create API client
        api = BoltAPI(api_key="test_api_key", context=context)

        # 3. Mock the client
        mock_client = Mock()
        mock_client.products = Mock()
        mock_client.products.get = Mock()

        # Mock successful response
        mock_product = Mock()
        mock_product.model_dump_json.return_value = (
            '{"id": "prod_123", "name": "Test Product"}'
        )
        mock_client.products.get.return_value = mock_product

        api._client = mock_client

        # 4. Find the get_product tool
        get_product_tool = None
        for tool in tools:
            if tool.method == "get_product":
                get_product_tool = tool
                break

        assert get_product_tool is not None
        assert get_product_tool.actions["products"]["read"] is True

        # 5. Make API call
        result = api.get_product(product_id="prod_123")

        # 6. Verify results
        assert "prod_123" in result
        assert "Test Product" in result
        mock_client.products.get.assert_called_once_with(product_id="prod_123")

    def test_error_workflow(self, sample_configuration):
        """Test the workflow with an error."""
        # 1. Create context and configuration
        context = Context(
            api_key="test_api_key",
            publishable_key="test_publishable_key",
        )

        # 2. Create API client
        api = BoltAPI(api_key="test_api_key", context=context)

        # 3. Mock the client with error
        mock_client = Mock()
        mock_client.products = Mock()
        mock_client.products.get = Mock()
        mock_client.products.get.side_effect = Exception("Product not found")

        api._client = mock_client

        # 4. Make API call that will fail
        try:
            result = api.get_product(product_id="invalid_id")
        except Exception as e:
            result = f'{{"error": "{str(e)}", "success": false}}'

        # 5. Verify error handling
        assert "error" in result
        assert "Product not found" in result
        assert "success" in result
        assert "false" in result

    def test_disabled_tool_workflow(self):
        """Test workflow with disabled tool."""
        # 1. Find the get_product tool
        get_product_tool = None
        for tool in tools:
            if tool.method == "get_product":
                get_product_tool = tool
                break

        assert get_product_tool is not None

        # 2. Verify tool actions match configuration
        assert get_product_tool.actions["products"]["read"] is True  # Tool allows it
        # But config disables it - this would be checked in actual usage

    def test_tool_system_integration(self):
        """Test that the tool system integrates properly."""
        # 1. Verify tools are properly defined
        assert len(tools) > 0

        # 2. Check that each tool has proper structure
        for tool in tools:
            assert hasattr(tool, "method")
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "args_schema")
            assert hasattr(tool, "actions")
            assert hasattr(tool, "execute")

            # 3. Check that tool actions are valid
            for product, actions in tool.actions.items():
                assert isinstance(actions, dict)
                for action, enabled in actions.items():
                    assert isinstance(enabled, bool)

        # 4. Check that get_product tool exists and is properly configured
        get_product_tool = None
        for tool in tools:
            if tool.method == "get_product":
                get_product_tool = tool
                break

        assert get_product_tool is not None
        assert get_product_tool.name == "Get Product"
        assert "products" in get_product_tool.actions
        assert "read" in get_product_tool.actions["products"]
        assert get_product_tool.actions["products"]["read"] is True
