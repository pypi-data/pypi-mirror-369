"""Real API validation tests for canvases tools."""

import pytest

from braze_mcp.models.canvases import CanvasListResponse
from braze_mcp.tools.canvases import get_canvas_list


@pytest.mark.real_api
class TestCanvasesRealAPI:
    """Real API tests for canvases tools."""

    @pytest.mark.asyncio
    async def test_get_canvas_list_basic(self, real_context):
        """Test get_canvas_list against real Braze API."""
        result = await get_canvas_list(real_context)

        # Validate return type is Pydantic model
        assert isinstance(result, CanvasListResponse), (
            f"Expected CanvasListResponse, got {type(result)}"
        )

        # Validate response structure
        assert hasattr(result, "canvases"), "Response should have canvases attribute"
        assert hasattr(result, "message"), "Response should have message attribute"

        # Validate data types
        assert isinstance(result.canvases, list), "Canvases should be a list"
        assert isinstance(result.message, str), "Message should be a string"

        # If canvases exist, validate structure
        if result.canvases:
            canvas = result.canvases[0]
            assert hasattr(canvas, "id"), "Canvas should have id attribute"
            assert hasattr(canvas, "name"), "Canvas should have name attribute"
            assert hasattr(canvas, "last_edited"), "Canvas should have last_edited attribute"

    @pytest.mark.asyncio
    async def test_get_canvas_list_with_parameters(self, real_context):
        """Test get_canvas_list with parameters against real Braze API."""
        result = await get_canvas_list(
            real_context, page=0, include_archived=False, sort_direction="desc"
        )

        # Validate return type is Pydantic model
        assert isinstance(result, CanvasListResponse), (
            f"Expected CanvasListResponse, got {type(result)}"
        )

        # Should still get valid response
        assert hasattr(result, "canvases"), "Response should have canvases attribute"
        assert hasattr(result, "message"), "Response should have message attribute"
