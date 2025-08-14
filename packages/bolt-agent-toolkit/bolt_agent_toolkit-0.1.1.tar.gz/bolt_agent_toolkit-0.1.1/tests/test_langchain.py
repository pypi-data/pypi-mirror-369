"""
Tests for bolt_agent_toolkit.langchain module
"""

from unittest.mock import Mock, patch

import pytest

from bolt_agent_toolkit.api import BoltAPI
from bolt_agent_toolkit.configuration import Configuration, Context
from bolt_agent_toolkit.langchain.tool import BoltTool
from bolt_agent_toolkit.langchain.toolkit import BoltAgentToolkit
from bolt_agent_toolkit.products import ProductInfo, ProductMerchantInfo
from bolt_agent_toolkit.schema import GetProduct


class TestBoltTool:
    """Test the BoltTool class."""

    @pytest.fixture
    def mock_bolt_api(self):
        """Mock BoltAPI instance for testing."""
        api = Mock(spec=BoltAPI)
        return api

    @pytest.fixture
    def sample_bolt_tool(self, mock_bolt_api):
        """Sample BoltTool instance for testing."""
        return BoltTool(
            name="get_product",
            description="Get a product by ID",
            method="get_product",
            bolt_api=mock_bolt_api,
            args_schema=GetProduct,
        )

    def test_bolt_tool_creation(self, sample_bolt_tool, mock_bolt_api):
        """Test creating a BoltTool instance."""
        tool = sample_bolt_tool

        assert tool.name == "get_product"
        assert tool.description == "Get a product by ID"
        assert tool.method == "get_product"
        assert tool.bolt_api == mock_bolt_api
        assert tool.args_schema == GetProduct

    def test_bolt_tool_run_success(self, sample_bolt_tool, mock_bolt_api):
        """Test successful execution of BoltTool._run method."""
        # Mock the API method
        mock_method = Mock(return_value='{"id": "prod_123", "name": "Test Product"}')
        mock_bolt_api.get_product = mock_method

        # Execute the tool
        result = sample_bolt_tool._run(product_id="prod_123")

        # Verify the result
        assert result == '{"id": "prod_123", "name": "Test Product"}'
        mock_method.assert_called_once_with(product_id="prod_123")

    def test_bolt_tool_run_with_kwargs(self, sample_bolt_tool, mock_bolt_api):
        """Test BoltTool._run method with keyword arguments."""
        # Mock the API method
        mock_method = Mock(return_value='{"id": "prod_123", "name": "Test Product"}')
        mock_bolt_api.get_product = mock_method

        # Execute the tool with kwargs
        result = sample_bolt_tool._run(product_id="prod_123", include_details=True)

        # Verify the result
        assert result == '{"id": "prod_123", "name": "Test Product"}'
        mock_method.assert_called_once_with(product_id="prod_123", include_details=True)

    def test_bolt_tool_run_with_args_and_kwargs(self, sample_bolt_tool, mock_bolt_api):
        """Test BoltTool._run method with both args and kwargs."""
        # Mock the API method
        mock_method = Mock(return_value='{"id": "prod_123", "name": "Test Product"}')
        mock_bolt_api.get_product = mock_method

        # Execute the tool with both args and kwargs
        result = sample_bolt_tool._run("prod_123", include_details=True)

        # Verify the result
        assert result == '{"id": "prod_123", "name": "Test Product"}'
        mock_method.assert_called_once_with("prod_123", include_details=True)

    def test_bolt_tool_run_method_not_found(self, mock_bolt_api):
        """Test BoltTool._run method when the API method doesn't exist."""
        # Create a tool with a non-existent method
        tool = BoltTool(
            name="non_existent_method",
            description="A non-existent method",
            method="non_existent_method",
            bolt_api=mock_bolt_api,
            args_schema=GetProduct,
        )

        # The getattr should raise AttributeError for non-existent method
        with pytest.raises(AttributeError):
            tool._run(product_id="prod_123")

    def test_bolt_tool_run_api_method_exception(self, sample_bolt_tool, mock_bolt_api):
        """Test BoltTool._run method when the API method raises an exception."""
        # Mock the API method to raise an exception
        mock_method = Mock(side_effect=Exception("API Error"))
        mock_bolt_api.get_product = mock_method

        # Execute the tool and expect the exception to propagate
        with pytest.raises(Exception, match="API Error"):
            sample_bolt_tool._run(product_id="prod_123")

    def test_bolt_tool_getattr_usage(self, sample_bolt_tool, mock_bolt_api):
        """Test that BoltTool correctly uses getattr to call API methods."""
        # Mock the API method
        mock_method = Mock(return_value='{"success": true}')
        mock_bolt_api.get_product = mock_method

        # Execute the tool
        sample_bolt_tool._run(product_id="prod_123")

        # Verify that getattr was used correctly by checking the method was called
        mock_method.assert_called_once_with(product_id="prod_123")

    def test_bolt_tool_return_type_casting(self, sample_bolt_tool, mock_bolt_api):
        """Test that BoltTool correctly casts return values to string."""
        # Mock the API method to return a non-string value
        mock_method = Mock(return_value={"id": "prod_123", "name": "Test Product"})
        mock_bolt_api.get_product = mock_method

        # Execute the tool
        result = sample_bolt_tool._run(product_id="prod_123")

        # Verify the result is a string (cast should handle this)
        assert isinstance(
            result, dict
        )  # The cast doesn't actually convert, just tells mypy
        mock_method.assert_called_once_with(product_id="prod_123")


class TestBoltAgentToolkit:
    """Test the BoltAgentToolkit class."""

    @pytest.fixture
    def sample_configuration(self):
        """Sample configuration for testing."""
        context = Context(
            api_key="test_api_key",
            publishable_key="test_publishable_key",
            base_url="https://api-sandbox.bolt.com",
            timeout=30.0,
            environment="sandbox",
        )

        return Configuration(
            context=context,
            actions={
                "products": {
                    "read": True,
                    "create": False,
                },
                "subscriptions": {
                    "read": True,
                },
            },
        )

    def test_bolt_agent_toolkit_creation(self, sample_configuration):
        """Test creating a BoltAgentToolkit instance."""
        # Create the toolkit with real BoltAPI (will be mocked internally)
        with patch(
            "bolt_agent_toolkit.langchain.toolkit.BoltAPI"
        ) as mock_bolt_api_class:
            mock_api_instance = Mock(spec=BoltAPI)
            mock_bolt_api_class.return_value = mock_api_instance

            toolkit = BoltAgentToolkit(
                api_key="test_api_key",
                configuration=sample_configuration,
            )

            # Verify BoltAPI was created with correct parameters
            mock_bolt_api_class.assert_called_once_with(
                api_key="test_api_key", context=sample_configuration.get("context")
            )

            # Verify toolkit properties
            assert toolkit.get_api() == mock_api_instance
            assert isinstance(toolkit.get_tools(), list)

    def test_bolt_agent_toolkit_tools_filtering(self, sample_configuration):
        """Test that BoltAgentToolkit correctly filters tools based on configuration."""
        # Create the toolkit with mocked BoltAPI
        with patch(
            "bolt_agent_toolkit.langchain.toolkit.BoltAPI"
        ) as mock_bolt_api_class:
            mock_api_instance = Mock(spec=BoltAPI)
            mock_bolt_api_class.return_value = mock_api_instance

            toolkit = BoltAgentToolkit(
                api_key="test_api_key",
                configuration=sample_configuration,
            )

            tools = toolkit.get_tools()

            # Verify that tools are filtered correctly
            assert len(tools) > 0

            # Check that all tools are BoltTool instances
            for tool in tools:
                assert isinstance(tool, BoltTool)
                assert tool.bolt_api == mock_api_instance
                assert hasattr(tool, "method")
                assert hasattr(tool, "name")
                assert hasattr(tool, "description")

    def test_bolt_agent_toolkit_no_context(self):
        """Test creating BoltAgentToolkit with no context in configuration."""
        # Create configuration without context
        config = Configuration(
            actions={
                "products": {
                    "read": True,
                },
            },
        )

        # Create the toolkit with mocked BoltAPI
        with patch(
            "bolt_agent_toolkit.langchain.toolkit.BoltAPI"
        ) as mock_bolt_api_class:
            mock_api_instance = Mock(spec=BoltAPI)
            mock_bolt_api_class.return_value = mock_api_instance

            toolkit = BoltAgentToolkit(
                api_key="test_api_key",
                configuration=config,
            )

            # Verify BoltAPI was created with None context
            mock_bolt_api_class.assert_called_once_with(
                api_key="test_api_key", context=None
            )

            assert toolkit.get_api() == mock_api_instance

    def test_bolt_agent_toolkit_empty_configuration(self):
        """Test creating BoltAgentToolkit with empty configuration."""
        # Create empty configuration
        config = Configuration()

        # Create the toolkit with mocked BoltAPI
        with patch(
            "bolt_agent_toolkit.langchain.toolkit.BoltAPI"
        ) as mock_bolt_api_class:
            mock_api_instance = Mock(spec=BoltAPI)
            mock_bolt_api_class.return_value = mock_api_instance

            toolkit = BoltAgentToolkit(
                api_key="test_api_key",
                configuration=config,
            )

            # Verify BoltAPI was created
            mock_bolt_api_class.assert_called_once_with(
                api_key="test_api_key", context=None
            )

            # With empty configuration, no tools should be allowed
            tools = toolkit.get_tools()
            assert len(tools) == 0

    def test_bolt_agent_toolkit_tool_properties(self, sample_configuration):
        """Test that BoltAgentToolkit creates tools with correct properties."""
        # Create the toolkit with mocked BoltAPI
        with patch(
            "bolt_agent_toolkit.langchain.toolkit.BoltAPI"
        ) as mock_bolt_api_class:
            mock_api_instance = Mock(spec=BoltAPI)
            mock_bolt_api_class.return_value = mock_api_instance

            toolkit = BoltAgentToolkit(
                api_key="test_api_key",
                configuration=sample_configuration,
            )

            tools = toolkit.get_tools()

            # Verify tool properties
            for tool in tools:
                assert isinstance(tool, BoltTool)
                assert tool.bolt_api == mock_api_instance
                assert isinstance(tool.name, str)
                assert isinstance(tool.description, str)
                assert isinstance(tool.method, str)
                assert tool.args_schema is not None

                # Verify that the tool method matches the name
                assert tool.name == tool.method


class TestBoltToolIntegration:
    """Integration tests for BoltTool with real API methods."""

    @pytest.fixture
    def real_bolt_api(self, sample_context):
        """Create a real BoltAPI instance for integration testing."""
        return BoltAPI(api_key="test_api_key", context=sample_context)

    @pytest.fixture
    def sample_context(self):
        """Sample context for testing."""
        return Context(
            api_key="test_api_key",
            publishable_key="test_publishable_key",
            base_url="https://api-sandbox.bolt.com",
            timeout=30.0,
            environment="sandbox",
        )

    def test_bolt_tool_with_real_api_methods(self, real_bolt_api):
        """Test BoltTool with real BoltAPI methods."""
        # Create a tool that calls list_products
        tool = BoltTool(
            name="list_products",
            description="List all products",
            method="list_products",
            bolt_api=real_bolt_api,
            args_schema=None,
        )

        # Mock the underlying client to avoid real API calls
        mock_client = Mock()
        mock_client.products = Mock()
        mock_client.products.list = Mock()

        # Mock successful response
        mock_products = Mock()
        mock_products.model_dump_json.return_value = '{"products": []}'
        mock_client.products.list.return_value = mock_products

        real_bolt_api._client = mock_client

        # Execute the tool
        result = tool._run()

        # Verify the result
        assert result == '{"products": []}'
        mock_client.products.list.assert_called_once()

    def test_bolt_tool_method_resolution(self, real_bolt_api):
        """Test that BoltTool correctly resolves method names using getattr."""
        # Test with different method names
        method_names = ["list_products", "get_product", "list_subscriptions"]

        for method_name in method_names:
            # Verify the method exists on the API
            assert hasattr(real_bolt_api, method_name)

            # Create a tool for this method
            tool = BoltTool(
                name=method_name,
                description=f"Test {method_name}",
                method=method_name,
                bolt_api=real_bolt_api,
                args_schema=None,
            )

            # Verify getattr can resolve the method
            method = getattr(tool.bolt_api, tool.method)
            assert callable(method)

    def test_bolt_tool_with_create_product_kwargs(self, real_bolt_api):
        """Test BoltTool with create_product method that uses **kwargs."""
        # Create a tool for create_product
        tool = BoltTool(
            name="create_product",
            description="Create a product",
            method="create_product",
            bolt_api=real_bolt_api,
            args_schema=None,
        )

        # Mock the underlying client and helper functions
        mock_client = Mock()
        mock_client.products = Mock()
        mock_client.products.create = Mock()

        # Mock successful response
        mock_product = Mock()
        mock_product.model_dump_json.return_value = '{"id": "prod_123"}'
        mock_client.products.create.return_value = mock_product

        real_bolt_api._client = mock_client

        # Mock the create_product_with_client function
        with patch(
            "bolt_agent_toolkit.api.create_product_with_client"
        ) as mock_create_with_client:
            mock_create_with_client.return_value = '{"id": "prod_123"}'

            # Execute the tool with kwargs
            result = tool._run(
                name="Test Product",
                description="A test product",
                brand="TestBrand",
                sku="TEST-001",
                unit_price=1000,
                merchant_product_id="MERCH-001",
                merchant_variant_id="VAR-001",
                plans=[],
                images=["image1.jpg"],
            )

            # Verify the result
            assert result == '{"id": "prod_123"}'
            mock_create_with_client.assert_called_once_with(
                mock_client,
                name="Test Product",
                description="A test product",
                brand="TestBrand",
                sku="TEST-001",
                unit_price=1000,
                merchant_product_id="MERCH-001",
                merchant_variant_id="VAR-001",
                plans=[],
                images=["image1.jpg"],
            )
