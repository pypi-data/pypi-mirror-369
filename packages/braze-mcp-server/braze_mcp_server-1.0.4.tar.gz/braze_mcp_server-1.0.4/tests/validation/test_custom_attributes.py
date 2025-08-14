"""Real API validation tests for custom attributes tools."""

import pytest

from braze_mcp.models.custom_attributes import CustomAttributesWithPagination
from braze_mcp.tools.custom_attributes import get_custom_attributes


@pytest.mark.real_api
class TestCustomAttributesRealAPI:
    """Real API tests for custom attributes tools."""

    @pytest.mark.asyncio
    async def test_get_custom_attributes_basic(self, real_context):
        """Test get_custom_attributes against real Braze API."""
        result = await get_custom_attributes(real_context)

        # Validate return type is Pydantic model
        assert isinstance(result, CustomAttributesWithPagination), (
            f"Expected CustomAttributesWithPagination, got {type(result)}"
        )

        # Validate response structure (Pydantic model with pagination)
        assert hasattr(result, "attributes"), "Response should have attributes attribute"
        assert hasattr(result, "message"), "Response should have message attribute"
        assert hasattr(result, "pagination_info"), "Response should have pagination_info attribute"

        # Validate data types
        assert isinstance(result.attributes, list), "Attributes should be a list"
        assert isinstance(result.message, str), "Message should be a string"

        # Validate pagination info
        assert hasattr(result.pagination_info, "current_page_count"), (
            "Should have current_page_count"
        )
        assert hasattr(result.pagination_info, "has_more_pages"), "Should have has_more_pages"
