"""Tool definitions for Bolt Agent Toolkit."""

from typing import Any, Callable, List

from .products import create_product_with_client
from .prompts import (
    CANCEL_SUBSCRIPTION_PROMPT,
    CREATE_PRODUCT_PROMPT,
    GET_PRODUCT_PROMPT,
    GET_SUBSCRIPTION_PROMPT,
    LIST_PLANS_PROMPT,
    LIST_PRODUCTS_PROMPT,
    LIST_SUBSCRIPTION_ORDERS_PROMPT,
    LIST_SUBSCRIPTIONS_PROMPT,
    PAUSE_SUBSCRIPTION_PROMPT,
    UNPAUSE_SUBSCRIPTION_PROMPT,
)
from .schema import (
    CancelSubscription,
    CreateProduct,
    GetProduct,
    GetSubscription,
    ListPlans,
    ListProducts,
    ListSubscriptionOrders,
    ListSubscriptions,
    PauseSubscription,
    Tool,
    UnpauseSubscription,
)


def _create_bolt_api_method_wrapper(method_name: str) -> Callable[..., Any]:
    """Create a wrapper function that calls the appropriate BoltAPI method."""

    def wrapper(bolt_api: Any, *args: Any, **kwargs: Any) -> Any:
        return getattr(bolt_api, method_name)(*args, **kwargs)

    return wrapper


def _create_product_wrapper(client: Any, **kwargs: Any) -> str:
    """Special wrapper for create_product that handles dataclass conversion."""
    return create_product_with_client(client, **kwargs)


tools: List[Tool] = [
    Tool(
        method="get_product",
        name="Get Product",
        description=GET_PRODUCT_PROMPT,
        args_schema=GetProduct,
        actions={
            "products": {
                "read": True,
            }
        },
        execute=_create_bolt_api_method_wrapper("get_product"),
    ),
    Tool(
        method="list_products",
        name="List Products",
        description=LIST_PRODUCTS_PROMPT,
        args_schema=ListProducts,
        actions={
            "products": {
                "read": True,
            }
        },
        execute=_create_bolt_api_method_wrapper("list_products"),
    ),
    Tool(
        method="create_product",
        name="Create Product",
        description=CREATE_PRODUCT_PROMPT,
        args_schema=CreateProduct,
        actions={
            "products": {
                "create": True,
            }
        },
        execute=_create_product_wrapper,
    ),
    Tool(
        method="get_subscription",
        name="Get Subscription",
        description=GET_SUBSCRIPTION_PROMPT,
        args_schema=GetSubscription,
        actions={
            "subscriptions": {
                "read": True,
            }
        },
        execute=_create_bolt_api_method_wrapper("get_subscription"),
    ),
    Tool(
        method="list_subscriptions",
        name="List Subscriptions",
        description=LIST_SUBSCRIPTIONS_PROMPT,
        args_schema=ListSubscriptions,
        actions={
            "subscriptions": {
                "read": True,
            }
        },
        execute=_create_bolt_api_method_wrapper("list_subscriptions"),
    ),
    Tool(
        method="pause_subscription",
        name="Pause Subscription",
        description=PAUSE_SUBSCRIPTION_PROMPT,
        args_schema=PauseSubscription,
        actions={
            "subscriptions": {
                "update": True,
            }
        },
        execute=_create_bolt_api_method_wrapper("pause_subscription"),
    ),
    Tool(
        method="unpause_subscription",
        name="Unpause Subscription",
        description=UNPAUSE_SUBSCRIPTION_PROMPT,
        args_schema=UnpauseSubscription,
        actions={
            "subscriptions": {
                "update": True,
            }
        },
        execute=_create_bolt_api_method_wrapper("unpause_subscription"),
    ),
    Tool(
        method="cancel_subscription",
        name="Cancel Subscription",
        description=CANCEL_SUBSCRIPTION_PROMPT,
        args_schema=CancelSubscription,
        actions={
            "subscriptions": {
                "delete": True,
            }
        },
        execute=_create_bolt_api_method_wrapper("cancel_subscription"),
    ),
    Tool(
        method="list_subscription_orders",
        name="List Subscription Orders",
        description=LIST_SUBSCRIPTION_ORDERS_PROMPT,
        args_schema=ListSubscriptionOrders,
        actions={
            "subscriptions": {
                "read": True,
            }
        },
        execute=_create_bolt_api_method_wrapper("list_subscription_orders"),
    ),
    Tool(
        method="list_plans",
        name="List Plans",
        description=LIST_PLANS_PROMPT,
        args_schema=ListPlans,
        actions={
            "plans": {
                "read": True,
            }
        },
        execute=_create_bolt_api_method_wrapper("list_plans"),
    ),
]
