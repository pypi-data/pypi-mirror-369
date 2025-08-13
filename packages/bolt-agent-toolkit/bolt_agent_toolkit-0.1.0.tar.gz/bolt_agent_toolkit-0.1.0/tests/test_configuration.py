"""
Tests for bolt_agent_toolkit.configuration module
"""

from bolt_agent_toolkit.configuration import (
    Configuration,
    Context,
    is_tool_allowed,
)


class TestContext:
    """Test the Context class."""

    def test_context_creation(self):
        """Test creating a Context instance."""
        context = Context(
            api_key="test_api_key",
            publishable_key="test_publishable_key",
            base_url="https://api-sandbox.bolt.com",
            timeout=30.0,
            environment="sandbox",
        )

        assert context.get("api_key") == "test_api_key"
        assert context.get("publishable_key") == "test_publishable_key"
        assert context.get("base_url") == "https://api-sandbox.bolt.com"
        assert context.get("timeout") == 30.0
        assert context.get("environment") == "sandbox"

    def test_context_defaults(self):
        """Test Context with default values."""
        context = Context(
            api_key="test_api_key",
            publishable_key="test_publishable_key",
        )

        assert context.get("api_key") == "test_api_key"
        assert context.get("publishable_key") == "test_publishable_key"
        assert context.get("base_url") is None
        assert context.get("timeout") is None
        assert context.get("environment") is None

    def test_context_get_method(self):
        """Test the get method of Context."""
        context = Context(
            api_key="test_api_key",
            publishable_key="test_publishable_key",
            timeout=60.0,
        )

        assert context.get("api_key") == "test_api_key"
        assert context.get("timeout") == 60.0
        assert context.get("non_existent") is None
        assert context.get("non_existent", "default") == "default"


class TestConfiguration:
    """Test the Configuration class."""

    def test_configuration_creation(self, sample_configuration):
        """Test creating a Configuration instance."""
        config = sample_configuration

        assert config.get("context").get("api_key") == "test_api_key"
        assert config.get("context").get("publishable_key") == "test_publishable_key"
        assert "products" in config.get("actions")
        assert "subscriptions" in config.get("actions")

    def test_configuration_get_method(self, sample_configuration):
        """Test the get method of Configuration."""
        config = sample_configuration

        # Test getting context
        context = config.get("context")
        assert isinstance(context, dict)  # TypedDict is a dict
        assert context.get("api_key") == "test_api_key"

        # Test getting actions
        actions = config.get("actions")
        assert isinstance(actions, dict)
        assert "products" in actions
        assert "subscriptions" in actions

        # Test getting non-existent key
        assert config.get("non_existent") is None
        assert config.get("non_existent", "default") == "default"

    def test_configuration_actions_structure(self, sample_configuration):
        """Test the structure of actions in Configuration."""
        config = sample_configuration
        actions = config.get("actions")

        # Test products actions
        assert "read" in actions["products"]
        assert "create" in actions["products"]
        assert actions["products"]["read"] is True
        assert actions["products"]["create"] is False

        # Test subscriptions actions
        assert "read" in actions["subscriptions"]
        assert actions["subscriptions"]["read"] is True


class TestIsToolAllowed:
    """Test the is_tool_allowed function."""

    def test_is_tool_allowed_with_valid_tool(self, sample_configuration, sample_tool):
        """Test is_tool_allowed with a valid tool."""
        config = sample_configuration

        # Test products.read (enabled)
        assert is_tool_allowed(sample_tool, config) is True

    def test_is_tool_allowed_with_disabled_tool(
        self, sample_configuration, sample_tool_disabled
    ):
        """Test is_tool_allowed with a disabled tool."""
        config = sample_configuration

        # Test products.create (disabled)
        assert is_tool_allowed(sample_tool_disabled, config) is False

    def test_is_tool_allowed_with_invalid_tool(self, sample_configuration):
        """Test is_tool_allowed with an invalid tool."""
        config = sample_configuration

        # Create a tool with non-existent resource
        from unittest.mock import Mock

        from bolt_agent_toolkit.schema import Tool

        invalid_tool = Tool(
            method="invalid_method",
            name="Invalid Tool",
            description="An invalid tool",
            args_schema=Mock(),
            actions={"non_existent": {"read": True}},
            execute=Mock(),
        )

        assert is_tool_allowed(invalid_tool, config) is False

    def test_is_tool_allowed_with_empty_actions(self):
        """Test is_tool_allowed with empty actions."""
        context = Context(
            api_key="test_api_key",
            publishable_key="test_publishable_key",
        )

        config = Configuration(
            context=context,
            actions={},
        )

        from unittest.mock import Mock

        from bolt_agent_toolkit.schema import Tool

        tool = Tool(
            method="get_product",
            name="Get Product",
            description="Get a product by ID",
            args_schema=Mock(),
            actions={"products": {"read": True}},
            execute=Mock(),
        )

        assert is_tool_allowed(tool, config) is False
