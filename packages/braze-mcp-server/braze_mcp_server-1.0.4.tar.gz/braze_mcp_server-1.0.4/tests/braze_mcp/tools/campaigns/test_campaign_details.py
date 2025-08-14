from unittest.mock import MagicMock, patch

import pytest

from braze_mcp.models.campaigns import CampaignDetails
from braze_mcp.tools.campaigns import get_campaign_details


class TestGetCampaignDetails:
    """Test get_campaign_details function"""

    @pytest.mark.asyncio
    async def test_get_campaign_details_success_with_default_paramters(
        self, mock_context, mock_braze_context, sample_campaign_details_data
    ):
        campaign_id = "test_campaign_id"
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=SuccessResponse(data=sample_campaign_details_data, headers={}),
            ) as mock_request:
                result = await get_campaign_details(mock_context, campaign_id)

                assert isinstance(result, CampaignDetails)
                assert result.message == "success"
                assert result.name == "Test Campaign Details"
                assert result.description == "Test campaign description"
                assert result.enabled
                assert not result.draft
                assert len(result.channels) == 2
                assert "email" in result.channels
                assert "push" in result.channels

                # Verify default parameters - new signature: client, base_url, url_path, params
                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client  # client
                assert call_args[0][1] == mock_braze_context.base_url  # base_url
                assert call_args[0][2] == "campaigns/details"  # url_path
                params = call_args[0][3]  # params
                assert params["campaign_id"] == campaign_id
                assert not params["post_launch_draft_version"]

    @pytest.mark.asyncio
    async def test_get_campaign_details_with_draft_version(
        self, mock_context, mock_braze_context, sample_campaign_details_data
    ):
        campaign_id = "test_campaign_id"
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=SuccessResponse(data=sample_campaign_details_data, headers={}),
            ) as mock_request:
                await get_campaign_details(
                    mock_context, campaign_id, post_launch_draft_version=True
                )

                # Verify parameters were passed correctly
                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client  # client
                assert call_args[0][1] == mock_braze_context.base_url  # base_url
                assert call_args[0][2] == "campaigns/details"  # url_path
                params = call_args[0][3]  # params
                assert params["campaign_id"] == campaign_id
                assert params["post_launch_draft_version"]

    @pytest.mark.asyncio
    async def test_get_campaign_details_request_failure(self, mock_context, mock_braze_context):
        campaign_id = "test_campaign_id"
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=FailureResponse(
                    data={"error": "Request failed"},
                    error=Exception("Request failed"),
                ),
            ):
                result = await get_campaign_details(mock_context, campaign_id)

                assert isinstance(result, dict)
                assert "error" in result
                assert result["error"] == "Request failed"

    @pytest.mark.asyncio
    async def test_get_campaign_details_parsing_error(self, mock_context, mock_braze_context):
        """Test get campaign details returns the raw response when the response fails schema validation"""
        campaign_id = "test_campaign_id"
        invalid_data = {"invalid": "data"}  # Missing required 'message' field
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
                    result = await get_campaign_details(mock_context, campaign_id)

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_campaign_details_empty_optional_fields(
        self, mock_context, mock_braze_context
    ):
        """Test campaign details schema validation with the minimal required fields"""
        campaign_id = "test_campaign_id"
        minimal_data = {
            "message": "success",
            "name": "Minimal Campaign",
            "description": None,
            "archived": None,
            "draft": None,
            "enabled": None,
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
                result = await get_campaign_details(mock_context, campaign_id)

                assert isinstance(result, CampaignDetails)
                assert result.message == "success"
                assert result.name == "Minimal Campaign"
                assert result.description is None
                assert result.archived is None
                assert result.draft is None
                assert result.enabled is None

    @pytest.mark.asyncio
    async def test_get_campaign_details_unexpected_response_type(
        self, mock_context, mock_braze_context
    ):
        """Test campaign details handles unexpected response type"""
        campaign_id = "test_campaign_id"

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
                    result = await get_campaign_details(mock_context, campaign_id)

                    assert isinstance(result, dict)
                    assert "error" in result
                    error_obj = result["error"]
                    assert error_obj["error_type"] == "unexpected_error"
                    assert "Unexpected response type:" in error_obj["message"]
                    mock_logger.assert_called_once_with(
                        f"Unexpected response type: {type(unexpected_response)}"
                    )
