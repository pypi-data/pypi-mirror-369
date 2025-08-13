from unittest.mock import patch

import pytest

from braze_mcp.models import (
    SegmentDataSeriesResponse,
    SegmentDetails,
    SegmentListResponse,
)
from braze_mcp.tools.segments import (
    get_segment_data_series,
    get_segment_details,
    get_segment_list,
)


@pytest.fixture
def sample_segment_list_data():
    return {
        "message": "success",
        "segments": [
            {
                "id": "segment_id_1",
                "name": "Test Segment 1",
                "analytics_tracking_enabled": True,
                "tags": ["tag1", "tag2"],
            },
            {
                "id": "segment_id_2",
                "name": "Test Segment 2",
                "analytics_tracking_enabled": False,
                "tags": ["tag3"],
            },
        ],
    }


@pytest.fixture
def sample_segment_data_series_data():
    return {
        "message": "success",
        "data": [
            {"time": "2025-01-01", "size": 10000},
            {"time": "2025-01-02", "size": 10500},
        ],
    }


@pytest.fixture
def sample_segment_details_data():
    return {
        "message": "success",
        "created_at": "2025-01-01T10:00:00Z",
        "updated_at": "2025-01-01T12:00:00Z",
        "name": "Test Segment Details",
        "description": "Users who have made a purchase",
        "text_description": "Segment for analyzing purchase behavior",
        "tags": ["analytics", "purchase"],
        "teams": ["Marketing", "Analytics"],
    }


class TestGetSegmentList:
    """Test get_segment_list function"""

    @pytest.mark.asyncio
    async def test_get_segment_list_success_with_default_parameters(
        self, mock_context, mock_braze_context, sample_segment_list_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.segments.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.segments.make_request",
                return_value=SuccessResponse(data=sample_segment_list_data, headers={}),
            ) as mock_request:
                result = await get_segment_list(mock_context)

                assert isinstance(result, SegmentListResponse)
                assert result.message == "success"
                assert len(result.segments) == 2
                assert result.segments[0].id == "segment_id_1"
                assert result.segments[0].name == "Test Segment 1"
                assert result.segments[0].analytics_tracking_enabled
                assert len(result.segments[0].tags) == 2
                assert result.segments[1].id == "segment_id_2"
                assert not result.segments[1].analytics_tracking_enabled

                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client
                assert call_args[0][1] == mock_braze_context.base_url
                assert call_args[0][2] == "segments/list"
                params = call_args[0][3]
                assert params["page"] == 0
                assert params["sort_direction"] == "desc"

    @pytest.mark.asyncio
    async def test_get_segment_list_success_with_custom_parameters(
        self, mock_context, mock_braze_context, sample_segment_list_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.segments.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.segments.make_request",
                return_value=SuccessResponse(data=sample_segment_list_data, headers={}),
            ) as mock_request:
                await get_segment_list(mock_context, page=2, sort_direction="desc")

                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["page"] == 2
                assert params["sort_direction"] == "desc"

    @pytest.mark.asyncio
    async def test_get_segment_list_request_failure(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.segments.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.segments.make_request",
                return_value=FailureResponse(
                    data={"error": "Request failed"},
                    error=Exception("Request failed"),
                ),
            ):
                result = await get_segment_list(mock_context)

                assert isinstance(result, dict)
                assert "error" in result
                assert result["error"] == "Request failed"

    @pytest.mark.asyncio
    async def test_get_segment_list_response_fails_parsing(self, mock_context, mock_braze_context):
        """Test get segment list returns the raw response when the response fails schema validation"""
        invalid_data = {"message": "success", "segments": [{"invalid": "data"}]}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.segments.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.segments.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ):
                with patch("braze_mcp.tools.segments.logger.exception") as mock_logger:
                    result = await get_segment_list(mock_context)

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()


class TestGetSegmentDataSeries:
    """Test get_segment_data_series function"""

    @pytest.mark.asyncio
    async def test_get_segment_data_series_success_with_required_parameters(
        self, mock_context, mock_braze_context, sample_segment_data_series_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        segment_id = "test_segment_id"

        with patch(
            "braze_mcp.tools.segments.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.segments.make_request",
                return_value=SuccessResponse(data=sample_segment_data_series_data, headers={}),
            ) as mock_request:
                result = await get_segment_data_series(
                    mock_context, segment_id=segment_id, length=14
                )

                assert isinstance(result, SegmentDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 2
                assert result.data[0].time == "2025-01-01"
                assert result.data[0].size == 10000
                assert result.data[1].time == "2025-01-02"
                assert result.data[1].size == 10500

                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client
                assert call_args[0][1] == mock_braze_context.base_url
                assert call_args[0][2] == "segments/data_series"
                params = call_args[0][3]
                assert params["segment_id"] == segment_id
                assert params["length"] == 14
                assert params["ending_at"] is None

    @pytest.mark.asyncio
    async def test_get_segment_data_series_success_with_all_parameters(
        self, mock_context, mock_braze_context, sample_segment_data_series_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        segment_id = "test_segment_id"

        with patch(
            "braze_mcp.tools.segments.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.segments.make_request",
                return_value=SuccessResponse(data=sample_segment_data_series_data, headers={}),
            ) as mock_request:
                await get_segment_data_series(
                    mock_context,
                    segment_id=segment_id,
                    length=30,
                    ending_at="2025-01-02T23:59:59-05:00",
                )

                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["segment_id"] == segment_id
                assert params["length"] == 30
                assert params["ending_at"] == "2025-01-02T23:59:59-05:00"

    @pytest.mark.asyncio
    async def test_get_segment_data_series_request_failure(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.segments.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.segments.make_request",
                return_value=FailureResponse(
                    data={"error": "Request failed"},
                    error=Exception("Request failed"),
                ),
            ):
                result = await get_segment_data_series(
                    mock_context, segment_id="test_id", length=14
                )

                assert isinstance(result, dict)
                assert "error" in result


class TestGetSegmentDetails:
    """Test get_segment_details function"""

    @pytest.mark.asyncio
    async def test_get_segment_details_success(
        self, mock_context, mock_braze_context, sample_segment_details_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        segment_id = "test_segment_id"

        with patch(
            "braze_mcp.tools.segments.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.segments.make_request",
                return_value=SuccessResponse(data=sample_segment_details_data, headers={}),
            ) as mock_request:
                result = await get_segment_details(mock_context, segment_id=segment_id)

                assert isinstance(result, SegmentDetails)
                assert result.message == "success"
                assert result.name == "Test Segment Details"
                assert result.description == "Users who have made a purchase"
                assert result.text_description == "Segment for analyzing purchase behavior"
                assert len(result.tags) == 2
                assert "analytics" in result.tags
                assert "purchase" in result.tags
                assert len(result.teams) == 2
                assert "Marketing" in result.teams
                assert "Analytics" in result.teams

                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client
                assert call_args[0][1] == mock_braze_context.base_url
                assert call_args[0][2] == "segments/details"
                params = call_args[0][3]
                assert params["segment_id"] == segment_id

    @pytest.mark.asyncio
    async def test_get_segment_details_request_failure(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.segments.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.segments.make_request",
                return_value=FailureResponse(
                    data={"error": "Request failed"},
                    error=Exception("Request failed"),
                ),
            ):
                result = await get_segment_details(mock_context, segment_id="test_segment_id")

                assert isinstance(result, dict)
                assert "error" in result

    @pytest.mark.asyncio
    async def test_get_segment_details_response_fails_parsing(
        self, mock_context, mock_braze_context
    ):
        invalid_data = {"message": "success", "invalid": "data"}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.segments.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.segments.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ):
                with patch("braze_mcp.tools.segments.logger.exception") as mock_logger:
                    result = await get_segment_details(mock_context, segment_id="test_segment_id")

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()
