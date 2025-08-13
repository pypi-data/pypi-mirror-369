"""Real API validation tests for events tools."""

import pytest

from braze_mcp.models.events import EventListResponse, EventsWithPagination
from braze_mcp.tools.events import get_events, get_events_list


@pytest.mark.real_api
class TestEventsRealAPI:
    """Real API tests for events tools."""

    @pytest.mark.asyncio
    async def test_get_events_list_basic(self, real_context):
        """Test get_events_list against real Braze API."""
        result = await get_events_list(real_context)

        # Validate return type is Pydantic model
        assert isinstance(result, EventListResponse), (
            f"Expected EventListResponse, got {type(result)}"
        )

        # Validate response structure (Pydantic model)
        assert hasattr(result, "events"), "Response should have events attribute"
        assert hasattr(result, "message"), "Response should have message attribute"

        # Validate data types
        assert isinstance(result.events, list), "Events should be a list"
        assert isinstance(result.message, str), "Message should be a string"

    @pytest.mark.asyncio
    async def test_get_events_with_pagination(self, real_context):
        """Test get_events with pagination against real Braze API."""
        result = await get_events(real_context)

        # Validate return type is Pydantic model
        assert isinstance(result, EventsWithPagination), (
            f"Expected EventsWithPagination, got {type(result)}"
        )

        # Validate response structure (Pydantic model with pagination)
        assert hasattr(result, "events"), "Response should have events attribute"
        assert hasattr(result, "message"), "Response should have message attribute"
        assert hasattr(result, "pagination_info"), "Response should have pagination_info attribute"

        # Validate data types
        assert isinstance(result.events, list), "Events should be a list"
        assert isinstance(result.message, str), "Message should be a string"

        # Validate pagination info
        assert hasattr(result.pagination_info, "current_page_count"), (
            "Should have current_page_count"
        )
        assert hasattr(result.pagination_info, "has_more_pages"), "Should have has_more_pages"
