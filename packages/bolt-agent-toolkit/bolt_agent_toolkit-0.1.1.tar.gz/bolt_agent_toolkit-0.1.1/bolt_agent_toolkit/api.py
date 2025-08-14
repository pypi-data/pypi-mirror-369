"""Util that calls Bolt."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from bolt_api_sdk import Bolt
from bolt_api_sdk.models import Security

from .configuration import Context
from .products import create_product_with_client


class BoltAPI:
    """Wrapper for Bolt API"""

    _context: Context
    _client: Bolt

    def __init__(self, api_key: str, context: Optional[Context] = None):
        self._context = context if context is not None else Context()
        security = Security(
            x_api_key=api_key,
            x_publishable_key=self._context.get("publishable_key"),
        )
        self._client = Bolt(
            security=security,
            server_url=self._context.get("base_url", "https://api.bolt.com"),
            timeout_ms=int(self._context.get("timeout") or 60.0) * 1000,
        )

    def create_meter_event(
        self, event: str, merchant_id: str, value: Optional[str] = None
    ) -> str:
        """Create a meter event for tracking."""
        meter_event_data: Dict[str, Any] = {
            "event_name": event,
            "payload": {
                "bolt_merchant_id": merchant_id,
            },
        }
        if value is not None:
            meter_event_data["payload"]["value"] = value

        # Send the event to Bolt when sdk feature is ready
        return json.dumps({"success": True, "event": meter_event_data})

    def list_products(self, **kwargs: Any) -> str:
        """
        List all products.

        Parameters:
            **kwargs: Additional parameters for filtering.

        Returns:
            str: JSON object with products key as list
                 of strings containing the list of products.
        """
        # NOTE: SDK errors out if no products are found.
        # This is because SDK cannot unmarshal null values to list.
        products = self._client.products.list(**kwargs)
        return products.model_dump_json()

    def get_product(self, product_id: str, **kwargs: Any) -> str:
        """
        Get a specific product by ID.

        Parameters:
            product_id (str): The ID of the product to retrieve.
            **kwargs: Additional parameters.

        Returns:
            str: JSON string containing the product data.
        """
        product = self._client.products.get(product_id=product_id, **kwargs)
        return product.model_dump_json()

    def create_product(self, **kwargs: Any) -> str:
        """
        Create a new product.

        Parameters:
            **kwargs: Product creation parameters including:
                - name (str): Product name.
                - description (str): Product description.
                - brand (str): Product brand.
                - sku (str): Product SKU.
                - unit_price (int): Product unit price in cents.
                - plans: Product plans configuration.
                - merchant_product_id (str): Merchant product ID.
                - merchant_variant_id (str): Merchant variant ID.
                - images (List[str]): List of product image URLs.

        Returns:
            str: JSON string containing the created product data.
        """
        return create_product_with_client(self._client, **kwargs)

    def list_subscriptions(self, **kwargs: Any) -> str:
        """
        List subscriptions with optional filtering.

        Parameters:
            **kwargs: Additional parameters for filtering subscriptions.

        Returns:
            str: JSON string containing the list of subscriptions.
        """
        # NOTE: SDK errors out if no subscriptions are found.
        # This is because SDK cannot unmarshal null values to list.
        subscriptions = self._client.subscriptions.list(**kwargs)
        return subscriptions.model_dump_json()

    def get_subscription(self, subscription_id: str, **kwargs: Any) -> str:
        """
        Get a specific subscription by ID.

        Parameters:
            subscription_id (str): The ID of the subscription to retrieve.
            **kwargs: Additional parameters.

        Returns:
            str: JSON string containing the subscription data.
        """
        subscription = self._client.subscriptions.get(
            subscription_id=subscription_id, **kwargs
        )
        return subscription.model_dump_json()

    def pause_subscription(self, subscription_id: str, **kwargs: Any) -> str:
        """
        Pause a subscription.

        Parameters:
            subscription_id (str): The ID of the subscription to pause.
            **kwargs: Additional parameters.

        Returns:
            str: JSON string containing the updated subscription data.
        """
        subscription = self._client.subscriptions.pause(
            subscription_id=subscription_id, **kwargs
        )
        return subscription.model_dump_json()

    def unpause_subscription(self, subscription_id: str, **kwargs: Any) -> str:
        """
        Unpause a subscription.

        Parameters:
            subscription_id (str): The ID of the subscription to unpause.
            **kwargs: Additional parameters.

        Returns:
            str: JSON string containing the updated subscription data.
        """
        subscription = self._client.subscriptions.unpause(
            subscription_id=subscription_id, **kwargs
        )
        return subscription.model_dump_json()

    def cancel_subscription(self, subscription_id: str, **kwargs: Any) -> str:
        """
        Cancel a subscription.

        Parameters:
            subscription_id (str): The ID of the subscription to cancel.
            **kwargs: Additional parameters.

        Returns:
            str: JSON string containing the updated subscription data.
        """
        subscription = self._client.subscriptions.cancel(
            subscription_id=subscription_id, **kwargs
        )
        return subscription.model_dump_json()

    def list_subscription_orders(
        self,
        subscription_ids: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        List subscription orders.

        Parameters:
            subscription_ids (str): Comma separated list of
                                    subscription IDs to list orders for.
            **kwargs: Additional parameters for filtering orders.

        Returns:
            str: JSON string containing the list of subscription orders.
        """
        # NOTE: SDK errors out if no orders are found.
        # This is because SDK cannot unmarshal null values to list.
        if subscription_ids:
            kwargs["subscription_ids"] = subscription_ids
        orders = self._client.subscription_orders.list(**kwargs)
        return orders.model_dump_json()

    def list_plans(self, merchant_product_id: str, **kwargs: Any) -> str:
        """
        List plans for a product.

        Parameters:
            merchant_product_id (str): The merchant product ID to list plans for.
            **kwargs: Additional parameters.

        Returns:
            str: JSON string containing the list of plans.
        """
        # NOTE: SDK errors out if no plans are found.
        # This is because SDK cannot unmarshal null values to list.
        plans = self._client.plans.list(
            merchant_product_id=merchant_product_id, **kwargs
        )
        return plans.model_dump_json()

    def close(self) -> None:
        """Synchronously close the client."""
        if self._client:
            self._client.close()
