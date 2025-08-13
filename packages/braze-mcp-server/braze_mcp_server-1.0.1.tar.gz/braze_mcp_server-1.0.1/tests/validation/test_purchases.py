"""Real API validation tests for purchases tools."""

import pytest

from braze_mcp.models.purchases import ProductListResponse, RevenueSeriesResponse
from braze_mcp.tools.purchases import get_product_list, get_revenue_series


@pytest.mark.real_api
class TestPurchasesRealAPI:
    """Real API tests for purchases tools."""

    @pytest.mark.asyncio
    async def test_get_product_list_basic(self, real_context):
        """Test get_product_list against real Braze API."""
        result = await get_product_list(real_context)

        # Validate return type is Pydantic model
        assert isinstance(result, ProductListResponse), (
            f"Expected ProductListResponse, got {type(result)}"
        )

        # Validate response structure (Pydantic model)
        assert hasattr(result, "products"), "Response should have products attribute"
        assert hasattr(result, "message"), "Response should have message attribute"

        # Validate data types
        assert isinstance(result.products, list), "Products should be a list"
        assert isinstance(result.message, str), "Message should be a string"

    @pytest.mark.asyncio
    async def test_get_revenue_series_basic(self, real_context):
        """Test get_revenue_series against real Braze API."""
        result = await get_revenue_series(real_context, length=7)

        # Validate return type is Pydantic model
        assert isinstance(result, RevenueSeriesResponse), (
            f"Expected RevenueSeriesResponse, got {type(result)}"
        )

        # Validate response structure (Pydantic model)
        assert hasattr(result, "data"), "Response should have data attribute"
        assert hasattr(result, "message"), "Response should have message attribute"

        # Validate data types
        assert isinstance(result.data, list), "Data should be a list"
        assert isinstance(result.message, str), "Message should be a string"
