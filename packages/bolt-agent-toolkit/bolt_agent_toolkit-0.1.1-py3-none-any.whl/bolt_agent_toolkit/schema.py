"""Schema definitions for Bolt Agent Toolkit."""

from typing import Any, Callable, Dict, List, Optional

from bolt_api_sdk.models import Plan
from pydantic import BaseModel, Field


class Tool(BaseModel):
    """Tool model for Bolt Agent Toolkit."""

    method: str
    name: str
    description: str
    args_schema: Any
    actions: Dict[str, Any]
    execute: Callable[..., Any]


class ListProducts(BaseModel):
    """Schema for the ``list_products`` operation."""


class GetProduct(BaseModel):
    """Schema for the ``get_product`` operation."""

    product_id: str = Field(
        ...,
        description="The ID of the product to retrieve.",
    )


class CreateProduct(BaseModel):
    """Schema for the ``create_product`` operation."""

    name: str = Field(
        ...,
        description="The name of the product.",
    )
    description: str = Field(
        ...,
        description="The description of the product.",
    )
    brand: str = Field(
        ...,
        description="The brand of the product.",
    )
    sku: str = Field(
        ...,
        description="The SKU of the product.",
    )
    unit_price: int = Field(
        ...,
        description="The unit price in cents.",
    )
    merchant_product_id: str = Field(
        ...,
        description="The merchant product ID.",
    )
    merchant_variant_id: str = Field(
        ...,
        description="The merchant variant ID.",
    )
    images: List[str] = Field(
        ...,
        description="List of product image URLs.",
    )
    plans: List[Plan] = Field(
        ...,
        description="List of plans for the product.",
    )


class DeleteProduct(BaseModel):
    """Schema for the ``delete_product`` operation."""

    product_id: str = Field(
        ...,
        description="The ID of the product to delete.",
    )


class ListSubscriptions(BaseModel):
    """Schema for the ``list_subscriptions`` operation."""

    customer_ids: Optional[str] = Field(
        None,
        description="Comma-separated list of customer IDs to filter by.",
    )
    emails: Optional[str] = Field(
        None,
        description="Comma-separated list of email addresses to filter by.",
    )
    product_ids: Optional[str] = Field(
        None,
        description="Comma-separated list of product IDs to filter by.",
    )
    plan_ids: Optional[str] = Field(
        None,
        description="Comma-separated list of plan IDs to filter by.",
    )


class GetSubscription(BaseModel):
    """Schema for the ``get_subscription`` operation."""

    subscription_id: str = Field(
        ...,
        description="The ID of the subscription to retrieve.",
    )


class PauseSubscription(BaseModel):
    """Schema for the ``pause_subscription`` operation."""

    subscription_id: str = Field(
        ...,
        description="The ID of the subscription to pause.",
    )


class UnpauseSubscription(BaseModel):
    """Schema for the ``unpause_subscription`` operation."""

    subscription_id: str = Field(
        ...,
        description="The ID of the subscription to unpause.",
    )


class CancelSubscription(BaseModel):
    """Schema for the ``cancel_subscription`` operation."""

    subscription_id: str = Field(
        ...,
        description="The ID of the subscription to cancel.",
    )


class ListSubscriptionOrders(BaseModel):
    """Schema for the ``list_subscription_orders`` operation."""

    subscription_ids: Optional[str] = Field(
        None,
        description="Comma-separated list of subscription IDs to filter by.",
    )


class ListPlans(BaseModel):
    """Schema for the ``list_plans`` operation."""

    merchant_product_id: str = Field(
        ...,
        description="The merchant product ID to list plans for.",
    )
    merchant_variant_id: Optional[str] = Field(
        None,
        description="The merchant variant ID to filter by.",
    )
