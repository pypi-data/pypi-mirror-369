from unittest.mock import MagicMock, patch

import pytest

from braze_mcp.models.events import EventsWithPagination
from braze_mcp.tools.events import get_events


class TestGetEvents:
    """Test get_events function"""

    @pytest.mark.asyncio
    async def test_get_events_success_without_cursor(
        self, mock_context, mock_braze_context, sample_events_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.events.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.events.make_request",
                return_value=SuccessResponse(data=sample_events_data, headers={}),
            ) as mock_request:
                result = await get_events(mock_context)

                assert isinstance(result, EventsWithPagination)
                assert result.message == "success"
                assert len(result.events) == 2
                assert result.events[0].name == "Test Event 1"
                assert result.events[0].description == "Description for test event 1"
                assert result.events[0].included_in_analytics_report is True
                assert result.events[0].status == "Active"
                assert result.events[0].tag_names == ["Tag One", "Tag Two"]
                assert result.events[1].name == "Test Event 2"
                assert result.events[1].included_in_analytics_report is False

                # Verify pagination info
                assert result.pagination_info.current_page_count == 2
                assert result.pagination_info.has_more_pages is False
                assert result.pagination_info.next_cursor is None
                assert result.pagination_info.max_per_page == 50

                # Verify parameters - params should be empty dict when cursor is None
                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client  # client
                assert call_args[0][1] == mock_braze_context.base_url  # base_url
                assert call_args[0][2] == "events"  # url_path
                params = call_args[0][3]  # params
                assert params == {}

    @pytest.mark.asyncio
    async def test_get_events_success_with_cursor(
        self, mock_context, mock_braze_context, sample_events_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        # Mock response with Link header to test pagination
        headers = {"link": '<https://rest.iad-01.braze.com/events?cursor=next123>; rel="next"'}

        with patch(
            "braze_mcp.tools.events.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.events.make_request",
                return_value=SuccessResponse(data=sample_events_data, headers=headers),
            ) as mock_request:
                result = await get_events(mock_context, cursor="c2tpcDow")

                assert isinstance(result, EventsWithPagination)
                # Verify pagination info with next cursor
                assert result.pagination_info.current_page_count == 2
                assert result.pagination_info.has_more_pages is True
                assert result.pagination_info.next_cursor == "next123"
                assert result.pagination_info.max_per_page == 50
                assert result.pagination_info.link_header == headers["link"]

                # Verify parameters were passed correctly
                call_args = mock_request.call_args
                params = call_args[0][3]  # params
                assert params == {"cursor": "c2tpcDow"}

    @pytest.mark.asyncio
    async def test_get_events_request_failure(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.events.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.events.make_request",
                return_value=FailureResponse(
                    data={"error": "Request failed"},
                    error=Exception("Request failed"),
                ),
            ):
                result = await get_events(mock_context)

                assert isinstance(result, dict)
                assert "error" in result
                assert result["error"] == "Request failed"

    @pytest.mark.asyncio
    async def test_get_events_response_fails_parsing(self, mock_context, mock_braze_context):
        """Test get events returns the raw response when the response fails schema validation"""
        invalid_data = {"message": "success", "events": [{"invalid": "data"}]}
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
                    result = await get_events(mock_context)

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_events_unexpected_response_type(self, mock_context, mock_braze_context):
        """Test events handles unexpected response type"""
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
                    result = await get_events(mock_context)

                    assert isinstance(result, dict)
                    assert "error" in result
                    error_obj = result["error"]
                    assert error_obj["error_type"] == "unexpected_error"
                    assert "Unexpected response type:" in error_obj["message"]
                    mock_logger.assert_called_once_with(
                        f"Unexpected response type: {type(unexpected_response)}"
                    )

    @pytest.mark.asyncio
    async def test_get_events_empty_optional_fields(self, mock_context, mock_braze_context):
        """Test events schema validation with minimal required fields"""
        minimal_data = {
            "message": "success",
            "events": [
                {
                    "name": "Minimal Event",
                    "description": "Test description",
                    "included_in_analytics_report": False,
                    "status": "Active",
                    "tag_names": [],
                }
            ],
        }
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.events.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.events.make_request",
                return_value=SuccessResponse(data=minimal_data, headers={}),
            ):
                result = await get_events(mock_context)

                assert isinstance(result, EventsWithPagination)
                assert result.message == "success"
                assert len(result.events) == 1
                assert result.events[0].name == "Minimal Event"
                assert result.events[0].description == "Test description"
                assert result.events[0].included_in_analytics_report is False
                assert result.events[0].status == "Active"
                assert result.events[0].tag_names == []

                # Verify pagination info
                assert result.pagination_info.current_page_count == 1
                assert result.pagination_info.has_more_pages is False
                assert result.pagination_info.next_cursor is None
                assert result.pagination_info.max_per_page == 50
