"""Agentic Prompt templates for Bolt Agent Toolkit tools."""

LIST_PRODUCTS_PROMPT = """
Retrieves a list of all products.

It takes no input arguments.
"""

GET_PRODUCT_PROMPT = """
Retrieves a product by its ID.

It takes one argument:
- product_id (int): ID of the product to retrieve.
"""

CREATE_PRODUCT_PROMPT = """
Creates a new product with associated plans.

It takes several arguments:
- name (str): Name of the product.
- description (str): Description of the product.
- brand (str): Brand of the product.
- sku (str): SKU of the product.
- unit_price (int): Unit price of the product in cents.
- merchant_product_id (str): ID for the product; if missing, global plans
                            are created.
- merchant_variant_id (str): ID for the product variant.
- images (List[str]): Array of image URLs for the product.
- plans (List[Plan]): List of plans for the product.
"""

LIST_SUBSCRIPTIONS_PROMPT = """
Retrieves a list of all subscriptions.

It takes optional arguments:
- customer_ids (str, optional): Comma-separated list of customer IDs to
                                filter subscriptions.
- emails (str, optional): Comma-separated list of email addresses to
                          filter subscriptions.
- product_ids (str, optional): Comma-separated list of product IDs to
                               filter subscriptions.
- plan_ids (str, optional): Comma-separated list of plan IDs to filter
                            subscriptions.
"""

GET_SUBSCRIPTION_PROMPT = """
Retrieves a subscription by its ID.

It takes one argument:
- subscription_id (int): ID of the subscription to retrieve.
"""

PAUSE_SUBSCRIPTION_PROMPT = """
Pauses a subscription by its ID.

It takes one argument:
- subscription_id (int): ID of the subscription to pause.
"""

UNPAUSE_SUBSCRIPTION_PROMPT = """
Unpauses a subscription by its ID.

It takes one argument:
- subscription_id (int): ID of the subscription to unpause.
"""

CANCEL_SUBSCRIPTION_PROMPT = """
Cancels a subscription by its ID.

It takes one argument:
- subscription_id (int): ID of the subscription to cancel.
"""

LIST_SUBSCRIPTION_ORDERS_PROMPT = """
Retrieves a list of all subscription orders.

It takes optional arguments:
- subscription_ids (str, optional): Comma-separated list of subscription
                                   IDs to filter orders.
"""

LIST_PLANS_PROMPT = """
Retrieves a list of plans.

It takes one required argument:
- merchant_product_id (str): ID of the product to retrieve plans for.

It takes one optional argument:
- merchant_variant_id (str, optional): ID of the product variant to
                                      retrieve plans for.
"""
