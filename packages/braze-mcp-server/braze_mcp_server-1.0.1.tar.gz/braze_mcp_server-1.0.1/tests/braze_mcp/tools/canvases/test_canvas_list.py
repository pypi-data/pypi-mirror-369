from unittest.mock import patch

import pytest

from braze_mcp.models.canvases import CanvasListResponse
from braze_mcp.tools.canvases import get_canvas_list


class TestGetCanvasList:
    """Test get_canvas_list function"""

    @pytest.mark.asyncio
    async def test_get_canvas_list_success_with_default_parameters(
        self, mock_context, mock_braze_context, sample_canvas_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=SuccessResponse(data=sample_canvas_data, headers={}),
            ) as mock_request:
                result = await get_canvas_list(mock_context)

                assert isinstance(result, CanvasListResponse)
                assert result.message == "success"
                assert len(result.canvases) == 2
                assert result.canvases[0].name == "Test Canvas 1"
                assert result.canvases[1].name == "Test Canvas 2"
                assert result.canvases[1].tags == ["tag1", "tag2"]

                # Verify default parameters
                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client  # http_client
                assert call_args[0][1] == mock_braze_context.base_url  # base_url
                assert call_args[0][2] == "canvas/list"  # url_path

                params = call_args[0][3]
                assert params["page"] == 0
                assert params["include_archived"] is False
                assert params["sort_direction"] == "desc"
                assert params["last_edit.time[gt]"] is None

    @pytest.mark.asyncio
    async def test_get_canvas_list_success_with_custom_parameters(
        self, mock_context, mock_braze_context, sample_canvas_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=SuccessResponse(data=sample_canvas_data, headers={}),
            ) as mock_request:
                result = await get_canvas_list(
                    mock_context,
                    page=1,
                    include_archived=True,
                    sort_direction="desc",
                    last_edit_time_gt="2020-06-28T23:59:59-5:00",
                )

                assert isinstance(result, CanvasListResponse)
                assert result.message == "success"
                assert len(result.canvases) == 2

                # Verify custom parameters
                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["page"] == 1
                assert params["include_archived"] is True
                assert params["sort_direction"] == "desc"
                assert params["last_edit.time[gt]"] == "2020-06-28T23:59:59-5:00"

    @pytest.mark.asyncio
    async def test_get_canvas_list_success_model_validation_fails(
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
                result = await get_canvas_list(mock_context)

                # Should return raw data when model validation fails
                assert result == invalid_data

    @pytest.mark.asyncio
    async def test_get_canvas_list_failure_response(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        error_data = {"message": "Invalid API key"}

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=FailureResponse(data=error_data, error=Exception("HTTP 401")),
            ):
                result = await get_canvas_list(mock_context)

                assert result == error_data

    @pytest.mark.asyncio
    async def test_get_canvas_list_unexpected_response(self, mock_context, mock_braze_context):
        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value="unexpected_response_type",
            ):
                result = await get_canvas_list(mock_context)

                assert "error" in result
                error_obj = result["error"]
                assert error_obj["error_type"] == "unexpected_error"
                assert "Unexpected response type:" in error_obj["message"]
