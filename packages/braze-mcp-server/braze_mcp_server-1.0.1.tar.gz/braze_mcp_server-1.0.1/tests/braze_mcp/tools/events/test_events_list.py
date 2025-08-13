from unittest.mock import MagicMock, patch

import pytest

from braze_mcp.models.events import EventListResponse
from braze_mcp.tools.events import get_events_list


class TestGetEventsList:
    """Test get_events_list function"""

    @pytest.mark.asyncio
    async def test_get_events_list_success_with_default_parameters(
        self, mock_context, mock_braze_context, sample_events_list_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.events.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.events.make_request",
                return_value=SuccessResponse(data=sample_events_list_data, headers={}),
            ) as mock_request:
                result = await get_events_list(mock_context)

                assert isinstance(result, EventListResponse)
                assert result.message == "success"
                assert len(result.events) == 3
                assert result.events[0] == "Event A"
                assert result.events[1] == "Event B"
                assert result.events[2] == "Event C"

                # Verify default parameters
                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client  # client
                assert call_args[0][1] == mock_braze_context.base_url  # base_url
                assert call_args[0][2] == "events/list"  # url_path
                params = call_args[0][3]  # params
                assert params["page"] == 0

    @pytest.mark.asyncio
    async def test_get_events_list_success_with_custom_page(
        self, mock_context, mock_braze_context, sample_events_list_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.events.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.events.make_request",
                return_value=SuccessResponse(data=sample_events_list_data, headers={}),
            ) as mock_request:
                await get_events_list(mock_context, page=3)

                # Verify parameters were passed correctly
                call_args = mock_request.call_args
                params = call_args[0][3]  # params
                assert params["page"] == 3

    @pytest.mark.asyncio
    async def test_get_events_list_request_failure(self, mock_context, mock_braze_context):
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
                result = await get_events_list(mock_context)

                assert isinstance(result, dict)
                assert "error" in result
                assert result["error"] == "Request failed"

    @pytest.mark.asyncio
    async def test_get_events_list_response_fails_parsing(self, mock_context, mock_braze_context):
        """Test get events list returns the raw response when the response fails schema validation"""
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
                    result = await get_events_list(mock_context)

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_events_list_unexpected_response_type(self, mock_context, mock_braze_context):
        """Test events list handles unexpected response type"""
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
                    result = await get_events_list(mock_context)

                    assert isinstance(result, dict)
                    assert "error" in result
                    error_obj = result["error"]
                    assert error_obj["error_type"] == "unexpected_error"
                    assert "Unexpected response type:" in error_obj["message"]
                    mock_logger.assert_called_once_with(
                        f"Unexpected response type: {type(unexpected_response)}"
                    )
