#!/usr/bin/env python3
"""
Bolt Agent Subscription Toolkit Tools

Explicit tool definitions for the Bolt Subscription MCP server.
"""

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, List, cast

from fastmcp import Context
from fastmcp.tools.tool import FunctionTool

from bolt_agent_toolkit.api import BoltAPI
from bolt_agent_toolkit.products import ProductInfo, ProductMerchantInfo


@dataclass
class BoltToolRegistry:
    """
    Registry class for storing the Bolt API client
    and tool decorator used by subscription tools.
    """

    bolt_api: BoltAPI
    tool_decorator: Callable[..., FunctionTool]


def set_bolt_api(api: BoltAPI) -> None:
    """Set the bolt API for all tools."""
    BoltToolRegistry.bolt_api = api


def set_tool_decorator(decorator_func: Callable[..., FunctionTool]) -> None:
    """Set the tool decorator function."""
    BoltToolRegistry.tool_decorator = decorator_func


def get_bolt_api() -> BoltAPI:
    """Get the bolt API."""
    if getattr(BoltToolRegistry, "bolt_api", None) is None:
        raise RuntimeError("Bolt API not initialized. Call set_bolt_api() first.")

    return BoltToolRegistry.bolt_api


def get_tool_decorator() -> Callable[..., FunctionTool]:
    """Get the tool decorator function."""
    if getattr(BoltToolRegistry, "tool_decorator", None) is None:
        raise RuntimeError(
            "Tool decorator not initialized. Call set_tool_decorator() first."
        )

    return BoltToolRegistry.tool_decorator


def _create_bolt_api_method_wrapper(
    method_name: str,
) -> Callable[..., Awaitable[str]]:
    """Create a wrapper function that calls the appropriate BoltAPI method."""

    async def wrapper(ctx: Context, *args: Any, **kwargs: Any) -> str:
        try:
            bolt_api = get_bolt_api()
            result = getattr(bolt_api, method_name)(*args, **kwargs)
            return cast(str, result)
        except Exception as e:
            await ctx.error(f"Failed to execute {method_name}: {str(e)}")
            raise

    return wrapper


def products_get(ctx: Context, product_id: str) -> Awaitable[str]:
    """Get a single product from Bolt API."""
    return _create_bolt_api_method_wrapper("get_product")(
        ctx,
        product_id=product_id,
    )


def products_list(ctx: Context) -> Awaitable[str]:
    """List all products from Bolt API."""
    return _create_bolt_api_method_wrapper("list_products")(ctx)


def products_create(
    ctx: Context,
    product_info: ProductInfo,
    merchant_info: ProductMerchantInfo,
) -> Awaitable[str]:
    """Create a new product."""
    return _create_bolt_api_method_wrapper("create_product")(
        ctx,
        **product_info.model_dump(),
        **merchant_info.model_dump(),
    )


def subscriptions_list(ctx: Context) -> Awaitable[str]:
    """List all subscriptions."""
    return _create_bolt_api_method_wrapper("list_subscriptions")(ctx)


def subscriptions_get(ctx: Context, subscription_id: str) -> Awaitable[str]:
    """Get a single subscription from Bolt API."""
    return _create_bolt_api_method_wrapper("get_subscription")(
        ctx,
        subscription_id=subscription_id,
    )


def subscriptions_pause(
    ctx: Context,
    subscription_id: str,
) -> Awaitable[str]:
    """Pause a subscription."""
    return _create_bolt_api_method_wrapper("pause_subscription")(
        ctx, subscription_id=subscription_id
    )


def subscriptions_unpause(
    ctx: Context,
    subscription_id: str,
) -> Awaitable[str]:
    """Unpause a subscription."""
    return _create_bolt_api_method_wrapper("unpause_subscription")(
        ctx, subscription_id=subscription_id
    )


def subscriptions_cancel(
    ctx: Context,
    subscription_id: str,
) -> Awaitable[str]:
    """Cancel a subscription."""
    return _create_bolt_api_method_wrapper("cancel_subscription")(
        ctx, subscription_id=subscription_id
    )


def plans_read(ctx: Context, merchant_product_id: str) -> Awaitable[str]:
    """List all plans for a product."""
    return _create_bolt_api_method_wrapper("list_plans")(
        ctx, merchant_product_id=merchant_product_id
    )


def orders_read(ctx: Context) -> Awaitable[str]:
    """List subscription orders."""
    return _create_bolt_api_method_wrapper("list_subscription_orders")(ctx)


# Comprehensive tool configuration
TOOL_CONFIG = {
    "products.read": [
        {
            "method": "list_products",
            "function": products_list,
            "description": "List all products from Bolt API",
        },
        {
            "method": "get_product",
            "function": products_get,
            "description": "Get a product from Bolt API",
        },
    ],
    "products.create": [
        {
            "method": "create_product",
            "function": products_create,
            "description": "Create a new product",
        },
    ],
    "subscriptions.read": [
        {
            "method": "list_subscriptions",
            "function": subscriptions_list,
            "description": "List all subscriptions",
        },
        {
            "method": "get_subscription",
            "function": subscriptions_get,
            "description": "Get a subscription",
        },
        {
            "method": "list_subscription_orders",
            "function": orders_read,
            "description": "List subscription orders",
        },
    ],
    "subscriptions.update": [
        {
            "method": "pause_subscription",
            "function": subscriptions_pause,
            "description": "Pause a subscription",
        },
        {
            "method": "unpause_subscription",
            "function": subscriptions_unpause,
            "description": "Unpause a subscription",
        },
    ],
    "subscriptions.delete": [
        {
            "method": "cancel_subscription",
            "function": subscriptions_cancel,
            "description": "Cancel a subscription",
        },
    ],
    "plans.read": [
        {
            "method": "list_plans",
            "function": plans_read,
            "description": "List all plans",
        },
    ],
}


def register_tools(tool_names: List[str]) -> None:
    """Register only the requested tools using the decorator."""
    decorator = get_tool_decorator()

    # Register each requested tool
    for tool_name in tool_names:
        methods = TOOL_CONFIG[tool_name]

        # Register each method as a separate tool
        for method_config in methods:
            if method_config["function"] is not None:
                decorator(  # type: ignore[operator]
                    name=method_config["method"],
                    description=method_config["description"],
                )(method_config["function"])
