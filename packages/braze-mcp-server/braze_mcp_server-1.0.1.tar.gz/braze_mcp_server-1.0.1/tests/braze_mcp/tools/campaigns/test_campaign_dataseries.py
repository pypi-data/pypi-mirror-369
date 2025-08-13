from unittest.mock import MagicMock, patch

import pytest

from braze_mcp.models.campaign_dataseries import CampaignDataSeriesResponse
from braze_mcp.tools.campaigns import get_campaign_dataseries


class TestGetCampaignDataSeries:
    """Test get_campaign_dataseries function"""

    @pytest.mark.asyncio
    async def test_get_campaign_dataseries_success_with_default_parameters(
        self, mock_context, mock_braze_context, sample_campaign_dataseries_response
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=SuccessResponse(data=sample_campaign_dataseries_response, headers={}),
            ) as mock_request:
                result = await get_campaign_dataseries(mock_context, "test-campaign-id", length=14)

                assert isinstance(result, CampaignDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 1
                assert result.data[0].time == "2024-01-01"
                assert result.data[0].unique_recipients == 1000
                assert result.data[0].revenue == 1250.50

                # Verify parameters - new signature: client, base_url, url_path, params
                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client  # client
                assert call_args[0][1] == mock_braze_context.base_url  # base_url
                assert call_args[0][2] == "campaigns/data_series"  # url_path
                params = call_args[0][3]  # params
                assert params["campaign_id"] == "test-campaign-id"
                assert params["length"] == 14

    @pytest.mark.asyncio
    async def test_get_campaign_dataseries_success_with_custom_parameters(
        self, mock_context, mock_braze_context, sample_campaign_dataseries_response
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=SuccessResponse(data=sample_campaign_dataseries_response, headers={}),
            ) as mock_request:
                await get_campaign_dataseries(
                    mock_context, "test-campaign-id", length=30, ending_at="2024-01-15"
                )

                # Verify parameters were passed correctly
                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client  # client
                assert call_args[0][1] == mock_braze_context.base_url  # base_url
                assert call_args[0][2] == "campaigns/data_series"  # url_path
                params = call_args[0][3]  # params
                assert params["campaign_id"] == "test-campaign-id"
                assert params["length"] == 30
                assert params["ending_at"] == "2024-01-15"

    @pytest.mark.asyncio
    async def test_get_campaign_dataseries_request_failure(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=FailureResponse(
                    data={"error": "Campaign not found"},
                    error=Exception("Campaign not found"),
                ),
            ):
                result = await get_campaign_dataseries(
                    mock_context, "invalid-campaign-id", length=7
                )

                assert isinstance(result, dict)
                assert "error" in result
                assert result["error"] == "Campaign not found"

    @pytest.mark.asyncio
    async def test_get_campaign_dataseries_response_fails_parsing(
        self, mock_context, mock_braze_context
    ):
        """Test get campaign DataSeries returns the raw response when the response fails schema validation"""
        invalid_data = {"message": "success", "invalid_field": "test"}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ):
                with patch("braze_mcp.tools.campaigns.logger.exception") as mock_logger:
                    result = await get_campaign_dataseries(
                        mock_context, "test-campaign-id", length=10
                    )

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_campaign_dataseries_empty_optional_fields(
        self, mock_context, mock_braze_context
    ):
        """Test campaign DataSeries schema validation with minimal required fields"""
        minimal_data = {
            "message": "success",
            "data": [{"time": "2024-01-01", "unique_recipients": 500, "messages": {}}],
        }
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=SuccessResponse(data=minimal_data, headers={}),
            ):
                result = await get_campaign_dataseries(mock_context, "test-campaign-id", length=7)

                assert isinstance(result, CampaignDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 1
                assert result.data[0].time == "2024-01-01"
                assert result.data[0].unique_recipients == 500
                assert result.data[0].conversions is None
                assert result.data[0].revenue is None

    @pytest.mark.asyncio
    async def test_get_campaign_dataseries_unexpected_response_type(
        self, mock_context, mock_braze_context
    ):
        """Test campaign dataseries handles unexpected response type"""

        # Create a mock object that isn't SuccessResponse or FailureResponse
        unexpected_response = MagicMock()
        unexpected_response.__class__.__name__ = "UnexpectedResponse"

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=unexpected_response,
            ):
                with patch("braze_mcp.tools.campaigns.logger.error") as mock_logger:
                    result = await get_campaign_dataseries(
                        mock_context, "test-campaign-id", length=5
                    )

                    assert isinstance(result, dict)
                    assert "error" in result
                    error_obj = result["error"]
                    assert error_obj["error_type"] == "unexpected_error"
                    assert "Unexpected response type:" in error_obj["message"]
                    mock_logger.assert_called_once_with(
                        f"Unexpected response type: {type(unexpected_response)}"
                    )

    @pytest.mark.asyncio
    async def test_get_campaign_dataseries_with_all_channel_types(
        self, mock_context, mock_braze_context, sample_all_channels_dataseries_response
    ):
        """Test campaign DataSeries with all supported message channel types"""
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=SuccessResponse(
                    data=sample_all_channels_dataseries_response, headers={}
                ),
            ):
                result = await get_campaign_dataseries(
                    mock_context, "comprehensive-campaign-id", length=1
                )

                assert isinstance(result, CampaignDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 1

                data_point = result.data[0]
                messages = data_point.messages

                # Verify all channel types are parsed correctly
                assert messages.ios_push is not None and len(messages.ios_push) == 1
                assert messages.android_push is not None and len(messages.android_push) == 1
                assert messages.kindle_push is not None and len(messages.kindle_push) == 1
                assert messages.web_push is not None and len(messages.web_push) == 1
                assert messages.email is not None and len(messages.email) == 1
                assert messages.sms is not None and len(messages.sms) == 1
                assert messages.whats_app is not None and len(messages.whats_app) == 1
                assert messages.content_cards is not None and len(messages.content_cards) == 1
                assert messages.in_app_message is not None and len(messages.in_app_message) == 1
                assert (
                    messages.trigger_in_app_message is not None
                    and len(messages.trigger_in_app_message) == 1
                )
                assert messages.webhook is not None and len(messages.webhook) == 1

                # Verify specific field values for new channel types
                assert messages.in_app_message[0].variation_api_id == "iam_1"
                assert messages.in_app_message[0].impressions == 120

                assert messages.trigger_in_app_message[0].variation_name == "Promo IAM"
                assert messages.trigger_in_app_message[0].revenue == 150.0

    @pytest.mark.asyncio
    async def test_get_campaign_dataseries_multivariate_response(
        self, mock_context, mock_braze_context, sample_multivariate_dataseries_response
    ):
        """Test campaign DataSeries with multivariate response format"""
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=SuccessResponse(
                    data=sample_multivariate_dataseries_response, headers={}
                ),
            ):
                result = await get_campaign_dataseries(
                    mock_context, "multivariate-campaign-id", length=7
                )

                assert isinstance(result, CampaignDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 1

                data_point = result.data[0]

                # Verify key multivariate fields
                assert data_point.conversions == 25
                assert data_point.revenue == 750.0
                assert data_point.unique_recipients == 1500

                # Verify trigger_in_app_message structure
                trigger_messages = data_point.messages.trigger_in_app_message
                assert trigger_messages is not None
                assert len(trigger_messages) == 3

                # Variation A - has impression/click data
                var_a = trigger_messages[0]
                assert var_a.variation_name == "Variation A"
                assert var_a.impressions == 800
                assert var_a.clicks == 80
                assert var_a.revenue == 300.0

                # Variation B - basic validation
                var_b = trigger_messages[1]
                assert var_b.variation_name == "Variation B"
                assert var_b.impressions == 700
                assert var_b.revenue == 250.0

                # Control Group - no impression/click data, has enrolled
                control = trigger_messages[2]
                assert control.variation_name == "Control Group"
                assert control.impressions is None
                assert control.clicks is None
                assert control.revenue == 200.0
                assert control.enrolled == 100

    @pytest.mark.asyncio
    async def test_get_campaign_dataseries_webhook_message_validation(
        self, mock_context, mock_braze_context, sample_webhook_dataseries_response
    ):
        """Test campaign DataSeries webhook message statistics validation"""
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=SuccessResponse(data=sample_webhook_dataseries_response, headers={}),
            ):
                result = await get_campaign_dataseries(
                    mock_context, "webhook-campaign-id", length=3
                )

                assert isinstance(result, CampaignDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 1

                data_point = result.data[0]
                webhook_messages = data_point.messages.webhook

                # Verify webhook messages are parsed correctly
                assert webhook_messages is not None
                assert len(webhook_messages) == 2

                # First webhook variation - has sent/errors values
                variant_1 = webhook_messages[0]
                assert variant_1.variation_name == "Variant 1"
                assert variant_1.variation_api_id == "7d7983ee-8cb6-456a-9c49-1e4df3c9fcfb"
                assert variant_1.sent == 0
                assert variant_1.errors == 0
                assert variant_1.revenue == 0.0
                assert variant_1.unique_recipients == 0
                assert variant_1.conversions == 0
                assert variant_1.enrolled is None

                # Control group - has null sent/errors values but has enrolled
                control_group = webhook_messages[1]
                assert control_group.variation_name == "Control Group"
                assert control_group.variation_api_id == "84fb1e3e-e4df-4c07-825b-a38242c193a0"
                assert control_group.sent is None
                assert control_group.errors is None
                assert control_group.revenue == 0.0
                assert control_group.unique_recipients == 0
                assert control_group.conversions == 0
                assert control_group.enrolled == 0

    @pytest.mark.asyncio
    async def test_get_campaign_dataseries_ios_push_extended_fields(
        self, mock_context, mock_braze_context, sample_ios_push_extended_response
    ):
        """Test campaign DataSeries iOS push message statistics with extended fields"""
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=SuccessResponse(data=sample_ios_push_extended_response, headers={}),
            ):
                result = await get_campaign_dataseries(
                    mock_context, "ios-extended-campaign-id", length=1
                )

                assert isinstance(result, CampaignDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 1

                data_point = result.data[0]
                ios_messages = data_point.messages.ios_push

                # Verify iOS push messages are parsed correctly
                assert ios_messages is not None
                assert len(ios_messages) == 2

                # Original variation - has all standard fields plus extended fields
                original = ios_messages[0]
                assert original.variation_name == "Original"
                assert original.variation_api_id == "695c1670-042d-4335-aa64-d119d64b0f11"
                assert original.sent == 0
                assert original.direct_opens == 0
                assert original.total_opens == 0
                assert original.bounces == 0
                assert original.body_clicks == 0
                assert original.revenue == 0.0
                assert original.unique_recipients == 0
                assert original.conversions == 0
                assert original.conversions_by_send_time == 0
                assert original.conversions1 == 0
                assert original.conversions2 == 0
                assert original.conversions3 == 0
                assert original.enrolled is None

                # Control group - has null values for core push fields but has enrolled
                control_group = ios_messages[1]
                assert control_group.variation_name == "Control Group"
                assert control_group.variation_api_id == "8374447a-d784-46d7-878a-40ee185f1840"
                assert control_group.sent is None
                assert control_group.direct_opens is None
                assert control_group.total_opens is None
                assert control_group.bounces is None
                assert control_group.body_clicks is None
                assert control_group.revenue == 0.0
                assert control_group.unique_recipients == 0
                assert control_group.conversions == 0
                assert control_group.enrolled == 0

    @pytest.mark.asyncio
    async def test_get_campaign_dataseries_webhook_in_all_channels(
        self, mock_context, mock_braze_context, sample_all_channels_dataseries_response
    ):
        """Test that webhook is included and validated in comprehensive channel response"""
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=SuccessResponse(
                    data=sample_all_channels_dataseries_response, headers={}
                ),
            ):
                result = await get_campaign_dataseries(
                    mock_context, "comprehensive-campaign-id", length=1
                )

                assert isinstance(result, CampaignDataSeriesResponse)
                data_point = result.data[0]
                messages = data_point.messages

                # Verify webhook message is now included and parsed
                assert messages.webhook is not None and len(messages.webhook) == 1
                webhook_message = messages.webhook[0]
                assert webhook_message.variation_name == "Test Webhook"
                assert webhook_message.variation_api_id == "webhook_123"
                assert webhook_message.sent == 25
                assert webhook_message.errors == 1
                assert webhook_message.revenue == 50.0
                assert webhook_message.conversions == 3
                assert webhook_message.conversions2 is None
                assert webhook_message.enrolled is None
