from unittest.mock import MagicMock, patch

import pytest

from braze_mcp.models import SendDataSeriesResponse
from braze_mcp.tools.sends import get_send_data_series


@pytest.fixture
def sample_send_dataseries_response():
    """Sample send data series API response"""
    return {
        "message": "success",
        "data": [
            {
                "time": "2024-01-01",
                "messages": {
                    "ios_push": [
                        {
                            "variation_name": "Variation A",
                            "sent": 1000,
                            "delivered": 980,
                            "undelivered": 20,
                            "delivery_failed": 5,
                            "direct_opens": 150,
                            "total_opens": 200,
                            "bounces": 10,
                            "body_clicks": 75,
                            "revenue": 500.0,
                            "unique_recipients": 950,
                            "conversions": 25,
                            "conversions_by_send_time": 20,
                            "conversions1": 10,
                            "conversions1_by_send_time": 8,
                            "conversions2": 5,
                            "conversions2_by_send_time": 4,
                            "conversions3": 2,
                            "conversions3_by_send_time": 1,
                        }
                    ]
                },
                "conversions_by_send_time": 20,
                "conversions1_by_send_time": 8,
                "conversions2_by_send_time": 4,
                "conversions3_by_send_time": 1,
                "conversions": 25,
                "conversions1": 10,
                "conversions2": 5,
                "conversions3": 2,
                "unique_recipients": 950,
                "revenue": 500.0,
            }
        ],
    }


class TestGetSendDataSeries:
    """Test get_send_data_series function"""

    @pytest.mark.asyncio
    async def test_get_send_data_series_success_with_required_parameters(
        self, mock_context, mock_braze_context, sample_send_dataseries_response
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.sends.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.sends.make_request",
                return_value=SuccessResponse(data=sample_send_dataseries_response, headers={}),
            ) as mock_request:
                result = await get_send_data_series(
                    mock_context,
                    campaign_id="test-campaign-id",
                    send_id="test-send-id",
                    length=14,
                )

                assert isinstance(result, SendDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 1
                assert result.data[0].time == "2024-01-01"
                assert result.data[0].unique_recipients == 950
                assert result.data[0].revenue == 500.0
                assert result.data[0].conversions == 25

                # Verify iOS push message statistics
                ios_push = result.data[0].messages.ios_push
                assert ios_push is not None
                assert len(ios_push) == 1
                assert ios_push[0].variation_name == "Variation A"
                assert ios_push[0].sent == 1000
                assert ios_push[0].delivered == 980
                assert ios_push[0].undelivered == 20
                assert ios_push[0].delivery_failed == 5
                assert ios_push[0].direct_opens == 150
                assert ios_push[0].total_opens == 200
                assert ios_push[0].revenue == 500.0

                # Verify request parameters
                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client
                assert call_args[0][1] == mock_braze_context.base_url
                assert call_args[0][2] == "sends/data_series"
                params = call_args[0][3]
                assert params["campaign_id"] == "test-campaign-id"
                assert params["send_id"] == "test-send-id"
                assert params["length"] == 14
                assert params["ending_at"] is None

    @pytest.mark.asyncio
    async def test_get_send_data_series_success_with_all_parameters(
        self, mock_context, mock_braze_context, sample_send_dataseries_response
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.sends.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.sends.make_request",
                return_value=SuccessResponse(data=sample_send_dataseries_response, headers={}),
            ) as mock_request:
                await get_send_data_series(
                    mock_context,
                    campaign_id="test-campaign-id",
                    send_id="test-send-id",
                    length=30,
                    ending_at="2024-01-15T23:59:59-05:00",
                )

                # Verify parameters were passed correctly
                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["campaign_id"] == "test-campaign-id"
                assert params["send_id"] == "test-send-id"
                assert params["length"] == 30
                assert params["ending_at"] == "2024-01-15T23:59:59-05:00"

    @pytest.mark.asyncio
    async def test_get_send_data_series_request_failure(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.sends.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.sends.make_request",
                return_value=FailureResponse(
                    data={"error": "Send not found"},
                    error=Exception("Send not found"),
                ),
            ):
                result = await get_send_data_series(
                    mock_context,
                    campaign_id="invalid-campaign-id",
                    send_id="invalid-send-id",
                    length=7,
                )

                assert isinstance(result, dict)
                assert "error" in result
                # error_data is already a standardized ErrorResponse from http.py
                assert result["error"] == "Send not found"

    @pytest.mark.asyncio
    async def test_get_send_data_series_response_fails_parsing(
        self, mock_context, mock_braze_context
    ):
        """Test get send data series returns the raw response when the response fails schema validation"""
        invalid_data = {"message": "success", "invalid_field": "test"}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.sends.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.sends.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ):
                with patch("braze_mcp.tools.sends.logger.exception") as mock_logger:
                    result = await get_send_data_series(
                        mock_context,
                        campaign_id="test-campaign-id",
                        send_id="test-send-id",
                        length=10,
                    )

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_send_data_series_empty_optional_fields(
        self, mock_context, mock_braze_context
    ):
        """Test send data series schema validation with minimal required fields"""
        minimal_data = {
            "message": "success",
            "data": [
                {
                    "time": "2024-01-01",
                    "messages": {},
                    "conversions": 0,
                    "unique_recipients": 100,
                }
            ],
        }
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.sends.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.sends.make_request",
                return_value=SuccessResponse(data=minimal_data, headers={}),
            ):
                result = await get_send_data_series(
                    mock_context,
                    campaign_id="test-campaign-id",
                    send_id="test-send-id",
                    length=7,
                )

                assert isinstance(result, SendDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 1
                assert result.data[0].time == "2024-01-01"
                assert result.data[0].unique_recipients == 100
                assert result.data[0].conversions == 0
                assert result.data[0].revenue is None

    @pytest.mark.asyncio
    async def test_get_send_data_series_unexpected_response_type(
        self, mock_context, mock_braze_context
    ):
        """Test send data series handles unexpected response type"""

        # Create a mock object that isn't SuccessResponse or FailureResponse
        unexpected_response = MagicMock()
        unexpected_response.__class__.__name__ = "UnexpectedResponse"

        with patch(
            "braze_mcp.tools.sends.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.sends.make_request",
                return_value=unexpected_response,
            ):
                with patch("braze_mcp.tools.sends.logger.error") as mock_logger:
                    result = await get_send_data_series(
                        mock_context,
                        campaign_id="test-campaign-id",
                        send_id="test-send-id",
                        length=5,
                    )

                    assert isinstance(result, dict)
                    assert "error" in result
                    assert result["success"] is False
                    assert result["error"]["error_type"] == "unexpected_error"
                    assert "Unexpected response type" in result["error"]["message"]
                    mock_logger.assert_called_once_with(
                        f"Unexpected response type: {type(unexpected_response)}"
                    )
