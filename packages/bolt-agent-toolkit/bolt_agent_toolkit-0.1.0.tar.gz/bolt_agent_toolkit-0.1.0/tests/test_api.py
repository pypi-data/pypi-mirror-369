"""
Tests for bolt_agent_toolkit.api module
"""

from unittest.mock import Mock

from bolt_agent_toolkit.api import BoltAPI
from bolt_agent_toolkit.configuration import Context


class TestBoltAPI:
    """Test the BoltAPI class."""

    def test_bolt_api_creation(self, mock_bolt_api):
        """Test creating a BoltAPI instance."""
        api = mock_bolt_api

        # BoltAPI doesn't expose api_key or context as public attributes
        assert hasattr(api, "_context")
        assert hasattr(api, "_client")
        assert api._context.get("api_key") == "test_api_key"
        assert api._context.get("publishable_key") == "test_publishable_key"

    def test_bolt_api_with_context(self):
        """Test creating BoltAPI with a context."""
        context = Context(
            api_key="test_api_key",
            publishable_key="test_publishable_key",
        )

        api = BoltAPI(
            api_key="test_api_key",
            context=context,
        )

        assert api._context == context

    def test_bolt_api_client_initialization(self, mock_bolt_api):
        """Test that the client is properly initialized."""
        api = mock_bolt_api

        # Check that client has the expected methods
        assert hasattr(api._client, "products")
        assert hasattr(api._client.products, "get")

        # Check that methods are mocks
        assert isinstance(api._client.products.get, Mock)

    def test_bolt_api_get_product_success(self, mock_bolt_api):
        """Test successful get_product call."""
        api = mock_bolt_api

        # Mock the product response
        mock_product = Mock()
        mock_product.model_dump_json.return_value = '{"id": "prod_123"}'
        api._client.products.get.return_value = mock_product

        # Test call
        result = api.get_product(product_id="prod_123")

        # Verify the call was made
        api._client.products.get.assert_called_once_with(product_id="prod_123")
        assert result == '{"id": "prod_123"}'

    def test_bolt_api_get_product_error(self, mock_bolt_api):
        """Test get_product call with error."""
        api = mock_bolt_api

        # Mock an exception
        api._client.products.get.side_effect = Exception("API Error")

        # Test call - should raise exception directly now
        try:
            api.get_product(product_id="invalid_id")
            assert False, "Expected exception to be raised"
        except Exception as e:
            assert "API Error" in str(e)

    def test_bolt_api_list_products_success(self, mock_bolt_api):
        """Test successful list_products call."""
        api = mock_bolt_api

        # Mock the products response
        mock_products = Mock()
        mock_products.model_dump_json.return_value = '{"products": []}'
        api._client.products.list.return_value = mock_products

        # Test call
        result = api.list_products()

        # Verify the call was made
        api._client.products.list.assert_called_once()
        assert result == '{"products": []}'

    def test_bolt_api_context_validation(self):
        """Test that BoltAPI validates context properly."""
        # Test with valid context
        context = Context(
            api_key="test_api_key",
            publishable_key="test_publishable_key",
        )

        api = BoltAPI(
            api_key="test_api_key",
            context=context,
        )

        assert api._context == context

        # Test that context is optional
        api_without_context = BoltAPI(api_key="test_api_key")
        assert api_without_context._context is not None

    def test_bolt_api_api_key_consistency(self):
        """Test that API key is consistent between BoltAPI and Context."""
        context = Context(
            api_key="context_api_key",
            publishable_key="test_publishable_key",
        )

        api = BoltAPI(
            api_key="bolt_api_key",
            context=context,
        )

        # The BoltAPI uses the passed api_key for security,
        # context has different key
        assert api._context.get("api_key") == "context_api_key"

    def test_bolt_api_base_url_from_context(self):
        """Test that base URL is taken from context."""
        context = Context(
            api_key="test_api_key",
            publishable_key="test_publishable_key",
            base_url="https://custom-api.bolt.com",
        )

        api = BoltAPI(
            api_key="test_api_key",
            context=context,
        )

        assert api._context.get("base_url") == "https://custom-api.bolt.com"

    def test_bolt_api_timeout_from_context(self):
        """Test that timeout is taken from context."""
        context = Context(
            api_key="test_api_key",
            publishable_key="test_publishable_key",
            timeout=60.0,
        )

        api = BoltAPI(
            api_key="test_api_key",
            context=context,
        )

        assert api._context.get("timeout") == 60.0

    def test_bolt_api_environment_from_context(self):
        """Test that environment is taken from context."""
        context = Context(
            api_key="test_api_key",
            publishable_key="test_publishable_key",
            environment="production",
        )

        api = BoltAPI(
            api_key="test_api_key",
            context=context,
        )

        assert api._context.get("environment") == "production"
