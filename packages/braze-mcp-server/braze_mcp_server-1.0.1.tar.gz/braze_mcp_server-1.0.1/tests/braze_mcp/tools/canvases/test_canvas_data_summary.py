from unittest.mock import patch

import pytest

from braze_mcp.models.canvases import CanvasDataSummaryResponse
from braze_mcp.tools.canvases import get_canvas_data_summary


class TestGetCanvasDataSummary:
    """Test get_canvas_data_summary function"""

    @pytest.mark.asyncio
    async def test_get_canvas_data_summary_success_with_default_parameters(
        self, mock_context, mock_braze_context, sample_canvas_data_summary
    ):
        """Test get_canvas_data_summary with minimal required parameters and all defaults."""
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=SuccessResponse(data=sample_canvas_data_summary, headers={}),
            ) as mock_request:
                result = await get_canvas_data_summary(
                    mock_context,
                    "test_canvas_id",
                    "2023-01-10T23:59:59Z",
                    length=7,
                )

                # Verify successful parsing
                assert isinstance(result, CanvasDataSummaryResponse)
                assert result.message == "success"
                assert result.data.name == "Test Canvas"

                # Verify API call parameters - all should use defaults
                call_args = mock_request.call_args
                assert call_args[0][2] == "canvas/data_summary"

                params = call_args[0][3]
                assert params["canvas_id"] == "test_canvas_id"
                assert params["ending_at"] == "2023-01-10T23:59:59Z"
                assert params["length"] == 7
                assert params["starting_at"] is None
                assert params["include_variant_breakdown"] is False
                assert params["include_step_breakdown"] is False
                assert params["include_deleted_step_data"] is False

    @pytest.mark.asyncio
    async def test_get_canvas_data_summary_success_with_starting_at(
        self, mock_context, mock_braze_context, sample_canvas_data_summary
    ):
        """Test get_canvas_data_summary using starting_at instead of length."""
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=SuccessResponse(data=sample_canvas_data_summary, headers={}),
            ) as mock_request:
                result = await get_canvas_data_summary(
                    mock_context,
                    "test_canvas_id",
                    "2023-01-10T23:59:59Z",
                    starting_at="2023-01-01T00:00:00Z",
                )

                # Verify successful parsing and key data fields
                assert isinstance(result, CanvasDataSummaryResponse)
                assert result.message == "success"
                assert result.data.total_stats.revenue == 1234.56
                assert result.data.total_stats.entries == 150

                # Verify starting_at parameter usage
                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["starting_at"] == "2023-01-01T00:00:00Z"
                assert params["length"] is None

    @pytest.mark.asyncio
    async def test_get_canvas_data_summary_success_with_all_breakdowns_enabled(
        self, mock_context, mock_braze_context, sample_canvas_data_summary
    ):
        """Test get_canvas_data_summary with all breakdown options enabled."""
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=SuccessResponse(data=sample_canvas_data_summary, headers={}),
            ) as mock_request:
                result = await get_canvas_data_summary(
                    mock_context,
                    "test_canvas_id",
                    "2023-01-10T23:59:59Z",
                    length=14,
                    include_variant_breakdown=True,
                    include_step_breakdown=True,
                    include_deleted_step_data=True,
                )

                # Verify successful parsing
                assert isinstance(result, CanvasDataSummaryResponse)
                assert result.message == "success"

                # Verify all breakdown parameters are enabled
                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["length"] == 14
                assert params["include_variant_breakdown"] is True
                assert params["include_step_breakdown"] is True
                assert params["include_deleted_step_data"] is True

    @pytest.mark.asyncio
    async def test_get_canvas_data_summary_missing_required_params(
        self, mock_context, mock_braze_context
    ):
        # Should return error when neither starting_at nor length is provided
        result = await get_canvas_data_summary(
            mock_context,
            "test_canvas_id",
            "2023-01-10T23:59:59Z",
        )

        assert "error" in result
        error_obj = result["error"]
        assert error_obj["error_type"] == "validation_error"
        assert error_obj["message"] == "Either starting_at or length parameter is required"

    @pytest.mark.asyncio
    async def test_get_canvas_data_summary_success_model_validation_fails(
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
                result = await get_canvas_data_summary(
                    mock_context,
                    "test_canvas_id",
                    "2023-01-10T23:59:59Z",
                    length=7,
                )

                # Should return raw data when model validation fails
                assert result == invalid_data

    @pytest.mark.asyncio
    async def test_get_canvas_data_summary_failure_response(self, mock_context, mock_braze_context):
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
                result = await get_canvas_data_summary(
                    mock_context,
                    "test_canvas_id",
                    "2023-01-10T23:59:59Z",
                    length=7,
                )

                assert result == error_data

    @pytest.mark.asyncio
    async def test_get_canvas_data_summary_unexpected_response(
        self, mock_context, mock_braze_context
    ):
        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value="unexpected_response_type",
            ):
                result = await get_canvas_data_summary(
                    mock_context,
                    "test_canvas_id",
                    "2023-01-10T23:59:59Z",
                    length=7,
                )

                assert "error" in result
                error_obj = result["error"]
                assert error_obj["error_type"] == "unexpected_error"
                assert "Unexpected response type:" in error_obj["message"]
