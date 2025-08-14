"""
Tests for bolt_agent_toolkit.modelcontextprotocol module
"""

from unittest.mock import Mock, patch

from bolt_agent_toolkit.modelcontextprotocol.toolkit import (
    ACCEPTED_TOOLS,
    BoltAgentToolkit,
    get_version_from_pyproject,
)


class TestBoltAgentToolkit:
    """Test the BoltAgentToolkit MCP implementation."""

    def test_toolkit_initialization_with_actions_setup(
        self, sample_configuration, mock_bolt_api
    ):
        """Test that toolkit properly sets up actions from tools."""
        with patch(
            "bolt_agent_toolkit.modelcontextprotocol.toolkit.BoltAPI",
            return_value=mock_bolt_api,
        ):
            toolkit = BoltAgentToolkit(
                api_key="test_api_key",
                tools=["products.read", "subscriptions.read"],
                configuration=sample_configuration,
            )

            # Test that actions are properly set up from tools
            actions = toolkit.configuration.get("actions", {})
            assert "products" in actions
            assert "subscriptions" in actions
            assert actions["products"]["read"] is True
            assert actions["subscriptions"]["read"] is True

    def test_toolkit_all_tools_registration(self, sample_configuration, mock_bolt_api):
        """Test that 'all' tools are properly registered."""
        with patch(
            "bolt_agent_toolkit.modelcontextprotocol.toolkit.BoltAPI",
            return_value=mock_bolt_api,
        ):
            with patch(
                "bolt_agent_toolkit.modelcontextprotocol.toolkit.register_all_tools"
            ) as mock_register:
                toolkit = BoltAgentToolkit(
                    api_key="test_api_key",
                    tools=["all"],
                    configuration=sample_configuration,
                )

                # Verify that register_all_tools was called with all accepted tools
                mock_register.assert_called_once()
                called_tools = mock_register.call_args[0][0]
                assert len(called_tools) == len(ACCEPTED_TOOLS)
                for tool in ACCEPTED_TOOLS:
                    assert tool in called_tools

    def test_toolkit_without_configuration(self, mock_bolt_api):
        """Test that toolkit works without configuration."""
        with patch(
            "bolt_agent_toolkit.modelcontextprotocol.toolkit.BoltAPI",
            return_value=mock_bolt_api,
        ):
            toolkit = BoltAgentToolkit(api_key="test_api_key", tools=["products.read"])

            # Test that default configuration is created
            assert toolkit.configuration is not None
            assert toolkit.api_key == "test_api_key"
            # Test that actions are set up even without initial configuration
            actions = toolkit.configuration.get("actions", {})
            assert isinstance(actions, dict)

    def test_tool_allowed_check(self, sample_configuration, mock_bolt_api):
        """Test that _is_tool_allowed correctly checks permissions."""
        with patch(
            "bolt_agent_toolkit.modelcontextprotocol.toolkit.BoltAPI",
            return_value=mock_bolt_api,
        ):
            toolkit = BoltAgentToolkit(
                api_key="test_api_key",
                tools=["products.read"],
                configuration=sample_configuration,
            )

            # Test allowed tool (products.read is True in sample_configuration)
            assert toolkit._is_tool_allowed("products.read") is True

            # Test allowed tool (products.create is True in sample_configuration)
            assert toolkit._is_tool_allowed("products.create") is True

            # Test disallowed tool (subscriptions.create is not in sample_configuration)
            assert toolkit._is_tool_allowed("subscriptions.create") is False

    def test_tool_registration_process(self, sample_configuration, mock_bolt_api):
        """Test the actual tool registration process."""
        with patch(
            "bolt_agent_toolkit.modelcontextprotocol.toolkit.BoltAPI",
            return_value=mock_bolt_api,
        ):
            with patch(
                "bolt_agent_toolkit.modelcontextprotocol.toolkit.register_all_tools"
            ) as mock_register:
                toolkit = BoltAgentToolkit(
                    api_key="test_api_key",
                    tools=["products.read", "products.create"],
                    configuration=sample_configuration,
                )

                # Verify that register_all_tools was called with the correct tools
                mock_register.assert_called_once()
                registered_tools = mock_register.call_args[0][0]
                assert "products.read" in registered_tools
                assert "products.create" in registered_tools

    def test_accepted_tools_list(self):
        """Test that ACCEPTED_TOOLS contains expected tools."""
        expected_tools = [
            "products.read",
            "products.create",
            "subscriptions.read",
            "subscriptions.update",
            "subscriptions.delete",
            "plans.read",
        ]

        for tool in expected_tools:
            assert tool in ACCEPTED_TOOLS

    def test_version_retrieval(self):
        """Test that get_version_from_pyproject returns a version string."""
        version = get_version_from_pyproject()
        assert isinstance(version, str)
        assert len(version) > 0
        assert "." in version  # Should contain version dots

    def test_toolkit_name_and_version(self, sample_configuration, mock_bolt_api):
        """Test that toolkit has correct name and version."""
        with patch(
            "bolt_agent_toolkit.modelcontextprotocol.toolkit.BoltAPI",
            return_value=mock_bolt_api,
        ):
            toolkit = BoltAgentToolkit(
                api_key="test_api_key",
                tools=["products.read"],
                configuration=sample_configuration,
            )

            assert toolkit.name == "Bolt"
            assert hasattr(toolkit, "version")
            assert isinstance(toolkit.version, str)

    def test_configuration_actions_setup(self, sample_configuration, mock_bolt_api):
        """Test that configuration actions are properly set up."""
        with patch(
            "bolt_agent_toolkit.modelcontextprotocol.toolkit.BoltAPI",
            return_value=mock_bolt_api,
        ):
            toolkit = BoltAgentToolkit(
                api_key="test_api_key",
                tools=["products.read"],
                configuration=sample_configuration,
            )

            actions = toolkit.configuration.get("actions", {})
            assert isinstance(actions, dict)
            assert "products" in actions
            # Test that actions are properly merged from tools
            assert "subscriptions" in actions
            assert actions["products"]["read"] is True
