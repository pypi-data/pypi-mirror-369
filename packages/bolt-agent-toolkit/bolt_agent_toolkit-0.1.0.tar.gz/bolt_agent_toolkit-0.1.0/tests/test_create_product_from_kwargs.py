"""Tests for create_product_from_kwargs function."""

import pytest

from bolt_agent_toolkit.products import (
    ProductInfo,
    ProductMerchantInfo,
    create_product_from_kwargs,
)


class TestCreateProductFromKwargs:
    """Test cases for create_product_from_kwargs function."""

    def test_create_product_from_kwargs_success(self):
        """Test successful creation with all required fields."""
        kwargs = {
            "name": "Test Product",
            "description": "A test product",
            "brand": "TestBrand",
            "sku": "TEST-001",
            "unit_price": 1000,
            "merchant_product_id": "MERCH-001",
            "merchant_variant_id": "VAR-001",
            "plans": [],
            "images": ["image1.jpg", "image2.jpg"],
        }

        product_info, merchant_info = create_product_from_kwargs(**kwargs)

        # Verify ProductInfo
        assert isinstance(product_info, ProductInfo)
        assert product_info.name == "Test Product"
        assert product_info.description == "A test product"
        assert product_info.brand == "TestBrand"
        assert product_info.sku == "TEST-001"
        assert product_info.unit_price == 1000

        # Verify ProductMerchantInfo
        assert isinstance(merchant_info, ProductMerchantInfo)
        assert merchant_info.merchant_product_id == "MERCH-001"
        assert merchant_info.merchant_variant_id == "VAR-001"
        assert merchant_info.plans == []
        assert merchant_info.images == ["image1.jpg", "image2.jpg"]

    def test_create_product_from_kwargs_with_extra_fields(self):
        """Test that extra fields are ignored."""
        kwargs = {
            "name": "Test Product",
            "description": "A test product",
            "brand": "TestBrand",
            "sku": "TEST-001",
            "unit_price": 1000,
            "merchant_product_id": "MERCH-001",
            "merchant_variant_id": "VAR-001",
            "plans": [],
            "images": ["image1.jpg"],
            "extra_field": "should be ignored",
            "another_extra": 123,
        }

        product_info, merchant_info = create_product_from_kwargs(**kwargs)

        # Should work fine and ignore extra fields
        assert product_info.name == "Test Product"
        assert merchant_info.merchant_product_id == "MERCH-001"

    def test_create_product_from_kwargs_missing_product_field(self):
        """Test error when missing ProductInfo field."""
        kwargs = {
            # Missing "name" field
            "description": "A test product",
            "brand": "TestBrand",
            "sku": "TEST-001",
            "unit_price": 1000,
            "merchant_product_id": "MERCH-001",
            "merchant_variant_id": "VAR-001",
            "plans": [],
            "images": ["image1.jpg"],
        }

        with pytest.raises(
            ValueError, match="Missing required fields for product creation: name"
        ):
            create_product_from_kwargs(**kwargs)

    def test_create_product_from_kwargs_missing_merchant_field(self):
        """Test error when missing ProductMerchantInfo field."""
        kwargs = {
            "name": "Test Product",
            "description": "A test product",
            "brand": "TestBrand",
            "sku": "TEST-001",
            "unit_price": 1000,
            # Missing "merchant_product_id" field
            "merchant_variant_id": "VAR-001",
            "plans": [],
            "images": ["image1.jpg"],
        }

        with pytest.raises(
            ValueError,
            match="Missing required fields for product creation: merchant_product_id",
        ):
            create_product_from_kwargs(**kwargs)

    def test_create_product_from_kwargs_missing_multiple_fields(self):
        """Test error when missing multiple fields."""
        kwargs = {
            "name": "Test Product",
            # Missing description, brand, sku, unit_price
            "merchant_product_id": "MERCH-001",
            # Missing merchant_variant_id, plans, images
        }

        with pytest.raises(ValueError) as exc_info:
            create_product_from_kwargs(**kwargs)

        error_message = str(exc_info.value)
        assert "Missing required fields for product creation:" in error_message
        # Should mention multiple missing fields
        assert "description" in error_message
        assert "brand" in error_message
        assert "sku" in error_message
        assert "unit_price" in error_message
        assert "merchant_variant_id" in error_message
        assert "plans" in error_message
        assert "images" in error_message

    def test_create_product_from_kwargs_with_complex_plans(self):
        """Test with complex plans data."""
        kwargs = {
            "name": "Subscription Product",
            "description": "A subscription product",
            "brand": "SubBrand",
            "sku": "SUB-001",
            "unit_price": 2000,
            "merchant_product_id": "MERCH-SUB-001",
            "merchant_variant_id": "VAR-SUB-001",
            "plans": [
                {"name": "Monthly", "price": 1000},
                {"name": "Yearly", "price": 10000},
            ],
            "images": ["sub1.jpg", "sub2.jpg", "sub3.jpg"],
        }

        product_info, merchant_info = create_product_from_kwargs(**kwargs)

        assert product_info.name == "Subscription Product"
        assert product_info.unit_price == 2000
        assert len(merchant_info.plans) == 2
        assert merchant_info.plans[0]["name"] == "Monthly"
        assert merchant_info.plans[1]["name"] == "Yearly"
        assert len(merchant_info.images) == 3

    def test_create_product_from_kwargs_empty_lists(self):
        """Test with empty plans and images lists."""
        kwargs = {
            "name": "Simple Product",
            "description": "A simple product",
            "brand": "SimpleBrand",
            "sku": "SIMPLE-001",
            "unit_price": 500,
            "merchant_product_id": "MERCH-SIMPLE-001",
            "merchant_variant_id": "VAR-SIMPLE-001",
            "plans": [],
            "images": [],
        }

        product_info, merchant_info = create_product_from_kwargs(**kwargs)

        assert product_info.name == "Simple Product"
        assert not merchant_info.plans
        assert not merchant_info.images

    def test_create_product_from_kwargs_field_types(self):
        """Test that field types are preserved correctly."""
        kwargs = {
            "name": "Type Test Product",
            "description": "Testing types",
            "brand": "TypeBrand",
            "sku": "TYPE-001",
            "unit_price": 1500,  # int
            "merchant_product_id": "MERCH-TYPE-001",
            "merchant_variant_id": "VAR-TYPE-001",
            "plans": [{"test": "plan"}],  # list
            "images": ["img1.jpg", "img2.jpg"],  # list of strings
        }

        product_info, merchant_info = create_product_from_kwargs(**kwargs)

        # Verify types are preserved
        assert isinstance(product_info.name, str)
        assert isinstance(product_info.unit_price, int)
        assert isinstance(merchant_info.plans, list)
        assert isinstance(merchant_info.images, list)
        assert all(isinstance(img, str) for img in merchant_info.images)
