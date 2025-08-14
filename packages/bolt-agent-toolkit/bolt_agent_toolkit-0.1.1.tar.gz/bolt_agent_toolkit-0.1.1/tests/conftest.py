"""
Test fixtures for bolt_agent_toolkit
"""

from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from bolt_agent_toolkit.api import BoltAPI
from bolt_agent_toolkit.configuration import Configuration, Context
from bolt_agent_toolkit.schema import Tool


class ProductSchema(BaseModel):
    """Test schema for product operations."""

    product_id: str


@pytest.fixture(name="mock_bolt_client")
def _mock_bolt_client():
    """Mock Bolt client for testing."""
    client = Mock()
    client.products = Mock()
    client.products.get = Mock()
    return client


@pytest.fixture(name="sample_context")
def _sample_context():
    """Sample context for testing."""
    return Context(
        api_key="test_api_key",
        publishable_key="test_publishable_key",
        base_url="https://api-sandbox.bolt.com",
        timeout=30.0,
        environment="sandbox",
    )


@pytest.fixture
def sample_configuration(sample_context):
    """Sample configuration for testing."""
    actions = {
        "products": {
            "read": True,
            "create": False,
        },
        "subscriptions": {
            "read": True,
        },
    }

    return Configuration(
        context=sample_context,
        actions=actions,
    )


@pytest.fixture
def mock_bolt_api(sample_context, mock_bolt_client):
    """Mock BoltAPI instance for testing."""
    api = BoltAPI(api_key="test_api_key", context=sample_context)
    api._client = mock_bolt_client
    return api


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "id": "prod_123",
        "name": "Test Product",
        "description": "A test product",
        "price": 1000,
        "currency": "USD",
    }


@pytest.fixture
def sample_tool():
    """Sample Tool object for testing."""
    return Tool(
        method="get_product",
        name="Get Product",
        description="Get a product by ID",
        args_schema=Mock(),  # Mock schema
        actions={"products": {"read": True}},
        execute=Mock(),  # Mock execute function
    )


@pytest.fixture
def sample_tool_disabled():
    """Sample Tool object with disabled action for testing."""
    return Tool(
        method="create_product",
        name="Create Product",
        description="Create a new product",
        args_schema=Mock(),  # Mock schema
        actions={"products": {"create": True}},
        execute=Mock(),  # Mock execute function
    )


@pytest.fixture
def mock_mcp_tools():
    """Mock MCP tools for testing."""
    return {
        "products.read": [
            {
                "method": "list_products",
                "function": Mock(),
                "description": "List products",
            }
        ],
        "subscriptions.read": [
            {
                "method": "list_subscriptions",
                "function": Mock(),
                "description": "List subscriptions",
            }
        ],
    }


@pytest.fixture
def mock_tool_decorator():
    """Mock tool decorator for testing."""
    return Mock()


@pytest.fixture
def mock_bolt_client_mcp():
    """Mock Bolt client specifically for MCP testing."""
    client = Mock()
    client.products = Mock()
    client.subscriptions = Mock()
    client.plans = Mock()
    return client


@pytest.fixture
def sample_tool_with_schema():
    """Sample Tool object with proper schema for testing."""
    return Tool(
        method="get_product",
        name="Get Product",
        description="Get a product by ID",
        args_schema=ProductSchema,
        actions={"products": {"read": True}},
        execute=Mock(),  # Mock execute function
    )
