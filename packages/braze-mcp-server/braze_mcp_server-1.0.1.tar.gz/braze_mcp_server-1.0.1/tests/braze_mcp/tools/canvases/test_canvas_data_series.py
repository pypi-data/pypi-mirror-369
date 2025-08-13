from unittest.mock import patch

import pytest

from braze_mcp.models.canvas_dataseries import CanvasDataSeriesResponse
from braze_mcp.tools.canvases import get_canvas_data_series


class TestGetCanvasDataSeries:
    """Test get_canvas_data_series function"""

    @pytest.mark.asyncio
    async def test_get_canvas_data_series_success_with_length(
        self, mock_context, mock_braze_context, sample_canvas_data_series
    ):
        """Test successful Canvas data series request with length parameter"""
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=SuccessResponse(data=sample_canvas_data_series, headers={}),
            ) as mock_request:
                result = await get_canvas_data_series(
                    mock_context,
                    canvas_id="test-canvas-id",
                    ending_at="2023-01-10T23:59:59-05:00",
                    length=7,
                    include_variant_breakdown=True,
                    include_step_breakdown=True,
                )

                assert isinstance(result, CanvasDataSeriesResponse)
                assert result.message == "success"
                assert result.data.name == "Test Canvas Data Series"
                assert len(result.data.stats) == 1

                # Check total stats
                stats = result.data.stats[0]
                assert stats.time == "2023-01-01"
                assert stats.total_stats.revenue is None
                assert stats.total_stats.conversions is None
                assert stats.total_stats.entries is None

                # Check variant stats
                assert stats.variant_stats is not None
                assert "variant-1-id" in stats.variant_stats
                variant = stats.variant_stats["variant-1-id"]
                assert variant.name == "Control"
                assert variant.revenue == 600.30
                assert variant.conversions == 15

                # Check step stats
                assert stats.step_stats is not None
                assert "step-1-id" in stats.step_stats
                step = stats.step_stats["step-1-id"]
                assert step.name == "Welcome Email"
                assert step.revenue == 500.25
                assert step.conversions == 12
                assert step.conversions_by_entry_time is None
                assert step.messages is None

                # Verify request parameters
                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["canvas_id"] == "test-canvas-id"
                assert params["ending_at"] == "2023-01-10T23:59:59-05:00"
                assert params["length"] == 7
                assert params["include_variant_breakdown"] is True
                assert params["include_step_breakdown"] is True

    @pytest.mark.asyncio
    async def test_get_canvas_data_series_success_with_starting_at(
        self, mock_context, mock_braze_context, sample_canvas_data_series
    ):
        """Test successful Canvas data series request with starting_at parameter"""
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=SuccessResponse(data=sample_canvas_data_series, headers={}),
            ) as mock_request:
                await get_canvas_data_series(
                    mock_context,
                    canvas_id="test-canvas-id",
                    ending_at="2023-01-10T23:59:59-05:00",
                    starting_at="2023-01-01T00:00:00-05:00",
                )

                # Verify parameters were passed correctly
                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["canvas_id"] == "test-canvas-id"
                assert params["ending_at"] == "2023-01-10T23:59:59-05:00"
                assert params["starting_at"] == "2023-01-01T00:00:00-05:00"
                assert params["length"] is None

    @pytest.mark.asyncio
    async def test_get_canvas_data_series_missing_required_parameter(
        self, mock_context, mock_braze_context
    ):
        """Test Canvas data series validation when neither starting_at nor length provided"""
        result = await get_canvas_data_series(
            mock_context,
            canvas_id="test-canvas-id",
            ending_at="2023-01-10T23:59:59-05:00",
        )

        assert isinstance(result, dict)
        assert "error" in result
        error_obj = result["error"]
        assert error_obj["error_type"] == "validation_error"
        assert error_obj["message"] == "Either starting_at or length parameter is required"

    @pytest.mark.asyncio
    async def test_get_canvas_data_series_request_failure(self, mock_context, mock_braze_context):
        """Test Canvas data series request failure handling"""
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=FailureResponse(
                    data={"error": "Canvas not found"},
                    error=Exception("Canvas not found"),
                ),
            ):
                result = await get_canvas_data_series(
                    mock_context,
                    canvas_id="invalid-canvas-id",
                    ending_at="2023-01-10T23:59:59-05:00",
                    length=7,
                )

                assert isinstance(result, dict)
                assert "error" in result
                assert result["error"] == "Canvas not found"

    @pytest.mark.asyncio
    async def test_get_canvas_data_series_response_fails_parsing(
        self, mock_context, mock_braze_context
    ):
        """Test Canvas data series returns the raw response when the response fails schema validation"""
        invalid_data = {"message": "success", "invalid_field": "test"}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ):
                with patch("braze_mcp.tools.canvases.logger.exception") as mock_logger:
                    result = await get_canvas_data_series(
                        mock_context,
                        canvas_id="test-canvas-id",
                        ending_at="2023-01-10T23:59:59-05:00",
                        length=7,
                    )

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_canvas_data_series_minimal_response(self, mock_context, mock_braze_context):
        """Test Canvas data series with minimal required fields"""
        minimal_data = {
            "message": "success",
            "data": {
                "name": "Minimal Canvas",
                "stats": [
                    {
                        "time": "2023-01-01",
                        "total_stats": {
                            "revenue": 0.0,
                            "conversions": 0,
                            "conversions_by_entry_time": 0,
                            "entries": 5,
                        },
                    }
                ],
            },
        }
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.canvases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.canvases.make_request",
                return_value=SuccessResponse(data=minimal_data, headers={}),
            ):
                result = await get_canvas_data_series(
                    mock_context,
                    canvas_id="test-canvas-id",
                    ending_at="2023-01-10T23:59:59-05:00",
                    length=1,
                )

                assert isinstance(result, CanvasDataSeriesResponse)
                assert result.message == "success"
                assert result.data.name == "Minimal Canvas"
                assert len(result.data.stats) == 1
                assert result.data.stats[0].variant_stats is None
                assert result.data.stats[0].step_stats is None
