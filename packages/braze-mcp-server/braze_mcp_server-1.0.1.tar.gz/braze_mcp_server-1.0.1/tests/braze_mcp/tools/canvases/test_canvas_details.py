from unittest.mock import patch

import pytest

from braze_mcp.models.canvases import CanvasDetails
from braze_mcp.tools.canvases import get_canvas_details


class TestGetCanvasDetails:
    """Test get_canvas_details function"""

    @pytest.mark.asyncio
    async def test_get_canvas_details_success_with_default_parameters(
        self, mock_context, mock_braze_context, sample_canvas_details_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=SuccessResponse(data=sample_canvas_details_data, headers={}),
            ) as mock_request:
                result = await get_canvas_details(mock_context, "test_canvas_id")

                assert isinstance(result, CanvasDetails)
                assert result.message == "success"
                assert result.name == "Test Canvas Details"
                assert result.description == "A test canvas for unit testing"
                assert result.enabled is True
                assert result.has_post_launch_draft is True
                assert len(result.variants) == 1
                assert len(result.steps) == 1
                assert result.steps[0].name == "Welcome Email"

                # Verify parameters
                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client  # http_client
                assert call_args[0][1] == mock_braze_context.base_url  # base_url
                assert call_args[0][2] == "canvas/details"  # url_path

                params = call_args[0][3]
                assert params["canvas_id"] == "test_canvas_id"
                assert params["post_launch_draft_version"] is False

    @pytest.mark.asyncio
    async def test_get_canvas_details_success_with_custom_parameters(
        self, mock_context, mock_braze_context, sample_canvas_details_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=SuccessResponse(data=sample_canvas_details_data, headers={}),
            ) as mock_request:
                result = await get_canvas_details(
                    mock_context,
                    "test_canvas_id",
                    post_launch_draft_version=True,
                )

                assert isinstance(result, CanvasDetails)
                assert result.message == "success"

                # Verify custom parameters
                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["canvas_id"] == "test_canvas_id"
                assert params["post_launch_draft_version"] is True

    @pytest.mark.asyncio
    async def test_get_canvas_details_success_model_validation_fails(
        self, mock_context, mock_braze_context
    ):
        from braze_mcp.utils.http import SuccessResponse

        invalid_data = {"invalid": "data"}

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ):
                result = await get_canvas_details(mock_context, "test_canvas_id")

                # Should return raw data when model validation fails
                assert result == invalid_data

    @pytest.mark.asyncio
    async def test_get_canvas_details_failure_response(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        error_data = {"message": "Canvas not found"}

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=FailureResponse(data=error_data, error=Exception("HTTP 404")),
            ):
                result = await get_canvas_details(mock_context, "test_canvas_id")

                assert result == error_data

    @pytest.mark.asyncio
    async def test_get_canvas_details_unexpected_response(self, mock_context, mock_braze_context):
        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value="unexpected_response_type",
            ):
                result = await get_canvas_details(mock_context, "test_canvas_id")

                assert "error" in result
                error_obj = result["error"]
                assert error_obj["error_type"] == "unexpected_error"
                assert "Unexpected response type:" in error_obj["message"]
