"""
This module contains product-related dataclasses and helper functions.
"""

from typing import Any, List

from pydantic import BaseModel


class ProductInfo(BaseModel):
    """Basic product information."""

    name: str
    description: str
    brand: str
    sku: str
    unit_price: int


class ProductMerchantInfo(BaseModel):
    """Merchant-specific product information."""

    merchant_product_id: str
    merchant_variant_id: str
    plans: Any  # Can be List[CreateProductPlan], List[CreateProductPlanTypedDict], etc.
    images: List[str]


def create_product_from_kwargs(
    **kwargs: Any,
) -> tuple[ProductInfo, ProductMerchantInfo]:
    """Helper function to create ProductInfo and ProductMerchantInfo from kwargs."""
    # Get field names from Pydantic model fields dynamically
    product_fields = set(ProductInfo.model_fields.keys())
    merchant_fields = set(ProductMerchantInfo.model_fields.keys())
    all_fields = product_fields.union(merchant_fields)

    missing_fields = [field for field in all_fields if field not in kwargs]
    if missing_fields:
        raise ValueError(
            f"Missing required fields for product creation: {', '.join(missing_fields)}"
        )

    # Filter kwargs for each model and use direct unpacking
    product_kwargs = {k: kwargs[k] for k in product_fields if k in kwargs}
    merchant_kwargs = {k: kwargs[k] for k in merchant_fields if k in kwargs}

    # Direct unpacking - much cleaner!
    product_info = ProductInfo(**product_kwargs)
    merchant_info = ProductMerchantInfo(**merchant_kwargs)

    return product_info, merchant_info


def create_product_with_client(client: Any, **kwargs: Any) -> str:
    """
    Create a product using any client that has a products.create method.

    This function abstracts the common product creation logic used by both
    BoltAPI and the tools wrapper functions.

    Args:
        client: Any client object with a products.create method (e.g., BoltAPI._client)
        **kwargs: Product creation parameters

    Returns:
        str: JSON string containing the created product data
    """
    product_info, merchant_info = create_product_from_kwargs(**kwargs)

    product = client.products.create(
        name=product_info.name,
        description=product_info.description,
        brand=product_info.brand,
        sku=product_info.sku,
        unit_price=product_info.unit_price,
        plans=merchant_info.plans,
        merchant_product_id=merchant_info.merchant_product_id,
        merchant_variant_id=merchant_info.merchant_variant_id,
        images=merchant_info.images,
    )
    return product.model_dump_json()  # type: ignore[no-any-return]
