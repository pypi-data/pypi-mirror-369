from unittest.mock import MagicMock, patch

import pytest

from braze_mcp.models.events import EventDataSeriesResponse
from braze_mcp.tools.events import get_events_data_series


class TestGetEventsDataSeries:
    """Test get_events_data_series function"""

    @pytest.mark.asyncio
    async def test_get_events_data_series_success_with_required_parameters(
        self, mock_context, mock_braze_context, sample_events_data_series_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.events.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.events.make_request",
                return_value=SuccessResponse(data=sample_events_data_series_data, headers={}),
            ) as mock_request:
                result = await get_events_data_series(mock_context, event="test_event", length=7)

                assert isinstance(result, EventDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 3
                assert result.data[0].time == "2024-01-01"
                assert result.data[0].count == 100
                assert result.data[1].time == "2024-01-02"
                assert result.data[1].count == 150

                # Verify parameters
                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client  # client
                assert call_args[0][1] == mock_braze_context.base_url  # base_url
                assert call_args[0][2] == "events/data_series"  # url_path
                params = call_args[0][3]  # params
                assert params["event"] == "test_event"
                assert params["length"] == 7
                assert params["unit"] == "day"  # default value
                assert params["ending_at"] is None
                assert params["app_id"] is None
                assert params["segment_id"] is None

    @pytest.mark.asyncio
    async def test_get_events_data_series_success_with_all_parameters(
        self, mock_context, mock_braze_context, sample_events_data_series_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.events.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.events.make_request",
                return_value=SuccessResponse(data=sample_events_data_series_data, headers={}),
            ) as mock_request:
                await get_events_data_series(
                    mock_context,
                    event="test_event",
                    length=24,
                    unit="hour",
                    ending_at="2024-12-10T23:59:59-05:00",
                    app_id="test_app_id",
                    segment_id="test_segment_id",
                )

                # Verify all parameters were passed correctly
                call_args = mock_request.call_args
                params = call_args[0][3]  # params
                assert params["event"] == "test_event"
                assert params["length"] == 24
                assert params["unit"] == "hour"
                assert params["ending_at"] == "2024-12-10T23:59:59-05:00"
                assert params["app_id"] == "test_app_id"
                assert params["segment_id"] == "test_segment_id"

    @pytest.mark.asyncio
    async def test_get_events_data_series_request_failure(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.events.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.events.make_request",
                return_value=FailureResponse(
                    data={"error": "Event not found"},
                    error=Exception("Event not found"),
                ),
            ):
                result = await get_events_data_series(
                    mock_context, event="nonexistent_event", length=7
                )

                assert isinstance(result, dict)
                assert "error" in result
                assert result["error"] == "Event not found"

    @pytest.mark.asyncio
    async def test_get_events_data_series_response_fails_parsing(
        self, mock_context, mock_braze_context
    ):
        """Test get events data series returns the raw response when the response fails schema validation"""
        invalid_data = {"message": "success", "invalid_field": "test"}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.events.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.events.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ):
                with patch("braze_mcp.tools.events.logger.exception") as mock_logger:
                    result = await get_events_data_series(
                        mock_context, event="test_event", length=7
                    )

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_events_data_series_unexpected_response_type(
        self, mock_context, mock_braze_context
    ):
        """Test events data series handles unexpected response type"""
        unexpected_response = MagicMock()
        unexpected_response.__class__.__name__ = "UnexpectedResponse"

        with patch(
            "braze_mcp.tools.events.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.events.make_request",
                return_value=unexpected_response,
            ):
                with patch("braze_mcp.tools.events.logger.error") as mock_logger:
                    result = await get_events_data_series(
                        mock_context, event="test_event", length=7
                    )

                    assert isinstance(result, dict)
                    assert "error" in result
                    error_obj = result["error"]
                    assert error_obj["error_type"] == "unexpected_error"
                    assert "Unexpected response type:" in error_obj["message"]
                    mock_logger.assert_called_once_with(
                        f"Unexpected response type: {type(unexpected_response)}"
                    )
