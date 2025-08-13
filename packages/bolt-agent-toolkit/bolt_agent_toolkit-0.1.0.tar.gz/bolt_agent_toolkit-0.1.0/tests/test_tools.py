"""
Tests for bolt_agent_toolkit.tools module
"""

from bolt_agent_toolkit.schema import Tool
from bolt_agent_toolkit.tools import tools


class TestTools:
    """Test the tools module."""

    def test_tools_list_not_empty(self):
        """Test that tools list is not empty."""
        assert len(tools) > 0
        assert isinstance(tools, list)

    def test_tools_structure(self):
        """Test the structure of tools."""
        for tool in tools:
            assert isinstance(tool, Tool)
            assert hasattr(tool, "method")
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "args_schema")
            assert hasattr(tool, "actions")
            assert hasattr(tool, "execute")

    def test_get_product_tool(self):
        """Test the get_product tool specifically."""
        # Find the get_product tool
        get_product_tool = None
        for tool in tools:
            if tool.method == "get_product":
                get_product_tool = tool
                break

        assert get_product_tool is not None
        assert get_product_tool.name == "Get Product"
        assert "product" in get_product_tool.description.lower()
        assert get_product_tool.actions["products"]["read"] is True

    def test_tool_execute_function(self):
        """Test that tool execute functions are callable."""
        for tool in tools:
            assert callable(tool.execute)

    def test_tool_actions_structure(self):
        """Test that tool actions have the correct structure."""
        for tool in tools:
            assert isinstance(tool.actions, dict)
            for product, actions in tool.actions.items():
                assert isinstance(actions, dict)
                for action, enabled in actions.items():
                    assert isinstance(enabled, bool)

    def test_tool_schema_validation(self):
        """Test that tool schemas are properly defined."""
        for tool in tools:
            assert tool.args_schema is not None
            # Check that the schema has the expected fields
            if tool.method == "get_product":
                # For Pydantic models, check the model fields
                schema_fields = tool.args_schema.model_fields.keys()
                assert "product_id" in schema_fields

    def test_tool_methods_are_unique(self):
        """Test that tool methods are unique."""
        methods = [tool.method for tool in tools]
        assert len(methods) == len(set(methods)), "Tool methods should be unique"
