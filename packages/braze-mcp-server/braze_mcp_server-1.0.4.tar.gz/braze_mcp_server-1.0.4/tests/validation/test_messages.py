"""Real API validation tests for messages tools."""

from datetime import UTC, datetime, timedelta

import pytest

from braze_mcp.models.messages import ScheduledBroadcastsResponse
from braze_mcp.tools.messages import get_scheduled_broadcasts


@pytest.mark.real_api
class TestMessagesRealAPI:
    """Real API tests for messages tools."""

    @pytest.mark.asyncio
    async def test_scheduled_broadcasts_comprehensive(self, real_context, validation_helper):
        """Test get_scheduled_broadcasts with comprehensive scenarios."""
        # Test with 30-day window (most common use case)
        end_time = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        result = await get_scheduled_broadcasts(real_context, end_time=end_time)

        # Validate response structure
        validation_helper.assert_pydantic_response(result, ScheduledBroadcastsResponse)
        validation_helper.assert_list_field(result, "scheduled_broadcasts")

        # Validate scheduled broadcasts structure
        assert len(result.scheduled_broadcasts) > 0, "Should have at least one scheduled broadcast"

    @pytest.mark.asyncio
    async def test_scheduled_broadcasts_error_handling(self, real_context, validation_helper):
        """Test error handling for scheduled broadcasts."""
        # Test with invalid date format
        result = await get_scheduled_broadcasts(real_context, end_time="invalid-date")

        # Should return error for invalid date
        validation_helper.assert_error_response(result, "for invalid date format")

        # Test with past date
        past_time = (datetime.now(UTC) - timedelta(days=1)).isoformat()
        result_past = await get_scheduled_broadcasts(real_context, end_time=past_time)

        # Should return empty results for past dates
        validation_helper.assert_pydantic_response(result_past, ScheduledBroadcastsResponse)
        assert isinstance(result_past.scheduled_broadcasts, list)
