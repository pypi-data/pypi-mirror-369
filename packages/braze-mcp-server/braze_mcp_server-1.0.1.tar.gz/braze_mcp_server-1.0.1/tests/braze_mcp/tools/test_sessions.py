from unittest.mock import patch

import pytest

from braze_mcp.models import SessionDataSeriesResponse
from braze_mcp.tools.sessions import get_session_data_series


@pytest.fixture
def sample_session_data_series_data():
    return {
        "message": "success",
        "data": [
            {"time": "2025-01-01", "sessions": 5000},
            {"time": "2025-01-02", "sessions": 5500},
        ],
    }


@pytest.fixture
def sample_session_data_series_hourly_data():
    return {
        "message": "success",
        "data": [
            {"time": "2025-01-01T10:00:00", "sessions": 200},
            {"time": "2025-01-01T11:00:00", "sessions": 250},
        ],
    }


class TestGetSessionDataSeries:
    """Test get_session_data_series function"""

    @pytest.mark.asyncio
    async def test_get_session_data_series_success_with_required_parameters(
        self, mock_context, mock_braze_context, sample_session_data_series_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.sessions.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.sessions.make_request",
                return_value=SuccessResponse(data=sample_session_data_series_data, headers={}),
            ) as mock_request:
                result = await get_session_data_series(mock_context, length=14)

                assert isinstance(result, SessionDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 2
                assert result.data[0].time == "2025-01-01"
                assert result.data[0].sessions == 5000
                assert result.data[1].time == "2025-01-02"
                assert result.data[1].sessions == 5500

                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client
                assert call_args[0][1] == mock_braze_context.base_url
                assert call_args[0][2] == "sessions/data_series"
                params = call_args[0][3]
                assert params["length"] == 14
                assert params["unit"] is None
                assert params["ending_at"] is None
                assert params["app_id"] is None
                assert params["segment_id"] is None

    @pytest.mark.asyncio
    async def test_get_session_data_series_success_with_all_parameters(
        self, mock_context, mock_braze_context, sample_session_data_series_hourly_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.sessions.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.sessions.make_request",
                return_value=SuccessResponse(
                    data=sample_session_data_series_hourly_data, headers={}
                ),
            ) as mock_request:
                result = await get_session_data_series(
                    mock_context,
                    length=24,
                    unit="hour",
                    ending_at="2025-01-02T23:59:59-05:00",
                    app_id="test_app_id",
                    segment_id="test_segment_id",
                )

                assert isinstance(result, SessionDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 2
                assert result.data[0].time == "2025-01-01T10:00:00"
                assert result.data[0].sessions == 200
                assert result.data[1].time == "2025-01-01T11:00:00"
                assert result.data[1].sessions == 250

                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["length"] == 24
                assert params["unit"] == "hour"
                assert params["ending_at"] == "2025-01-02T23:59:59-05:00"
                assert params["app_id"] == "test_app_id"
                assert params["segment_id"] == "test_segment_id"

    @pytest.mark.asyncio
    async def test_get_session_data_series_success_with_day_unit(
        self, mock_context, mock_braze_context, sample_session_data_series_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.sessions.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.sessions.make_request",
                return_value=SuccessResponse(data=sample_session_data_series_data, headers={}),
            ) as mock_request:
                await get_session_data_series(mock_context, length=7, unit="day")

                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["length"] == 7
                assert params["unit"] == "day"

    @pytest.mark.asyncio
    async def test_get_session_data_series_request_failure(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.sessions.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.sessions.make_request",
                return_value=FailureResponse(
                    data={"error": "Request failed"},
                    error=Exception("Request failed"),
                ),
            ):
                result = await get_session_data_series(mock_context, length=14)

                assert isinstance(result, dict)
                assert "error" in result
                assert result["error"] == "Request failed"

    @pytest.mark.asyncio
    async def test_get_session_data_series_response_fails_parsing(
        self, mock_context, mock_braze_context
    ):
        """Test get session data series returns the raw response when the response fails schema validation"""
        invalid_data = {"message": "success", "data": [{"invalid": "data"}]}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.sessions.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.sessions.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ):
                with patch("braze_mcp.tools.sessions.logger.exception") as mock_logger:
                    result = await get_session_data_series(mock_context, length=14)

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session_data_series_with_app_id_only(
        self, mock_context, mock_braze_context, sample_session_data_series_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.sessions.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.sessions.make_request",
                return_value=SuccessResponse(data=sample_session_data_series_data, headers={}),
            ) as mock_request:
                await get_session_data_series(mock_context, length=30, app_id="test_app_id")

                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["length"] == 30
                assert params["app_id"] == "test_app_id"
                assert params["segment_id"] is None

    @pytest.mark.asyncio
    async def test_get_session_data_series_with_segment_id_only(
        self, mock_context, mock_braze_context, sample_session_data_series_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.sessions.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.sessions.make_request",
                return_value=SuccessResponse(data=sample_session_data_series_data, headers={}),
            ) as mock_request:
                await get_session_data_series(mock_context, length=10, segment_id="test_segment_id")

                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["length"] == 10
                assert params["app_id"] is None
                assert params["segment_id"] == "test_segment_id"
