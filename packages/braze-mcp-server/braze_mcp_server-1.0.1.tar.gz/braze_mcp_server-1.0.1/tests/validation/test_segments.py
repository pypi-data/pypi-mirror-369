"""Real API validation tests for segments tools."""

import pytest

from braze_mcp.models.segments import SegmentListResponse
from braze_mcp.tools.segments import get_segment_list


@pytest.mark.real_api
class TestSegmentsRealAPI:
    """Real API tests for segments tools."""

    @pytest.mark.asyncio
    async def test_get_segment_list_basic(self, real_context):
        """Test get_segment_list against real Braze API."""
        result = await get_segment_list(real_context)

        # Validate return type is Pydantic model
        assert isinstance(result, SegmentListResponse), (
            f"Expected SegmentListResponse, got {type(result)}"
        )

        # Validate response structure (Pydantic model)
        assert hasattr(result, "segments"), "Response should have segments attribute"
        assert hasattr(result, "message"), "Response should have message attribute"

        # Validate data types
        assert isinstance(result.segments, list), "Segments should be a list"
        assert isinstance(result.message, str), "Message should be a string"

        # If segments exist, validate structure
        if result.segments:
            segment = result.segments[0]
            assert hasattr(segment, "id"), "Segment should have id attribute"
            assert hasattr(segment, "name"), "Segment should have name attribute"

    @pytest.mark.asyncio
    async def test_get_segment_list_with_parameters(self, real_context):
        """Test get_segment_list with parameters against real Braze API."""
        result = await get_segment_list(real_context, page=0, sort_direction="desc")

        # Validate return type is Pydantic model
        assert isinstance(result, SegmentListResponse), (
            f"Expected SegmentListResponse, got {type(result)}"
        )

        # Should still get valid response
        assert hasattr(result, "segments"), "Response should have segments attribute"
        assert hasattr(result, "message"), "Response should have message attribute"
