from unittest.mock import MagicMock, patch

import pytest

from braze_mcp.models.campaigns import CampaignListResponse
from braze_mcp.tools.campaigns import get_campaign_list


class TestGetCampaignList:
    """Test get_campaign_list function"""

    @pytest.mark.asyncio
    async def test_get_campaign_list_success_with_default_parameters(
        self, mock_context, mock_braze_context, sample_campaign_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=SuccessResponse(data=sample_campaign_data, headers={}),
            ) as mock_request:
                result = await get_campaign_list(mock_context)

                assert isinstance(result, CampaignListResponse)
                assert result.message == "success"
                assert len(result.campaigns) == 2
                assert result.campaigns[0].name == "Test Campaign 1"
                assert result.campaigns[1].name == "Test Campaign 2"

                # Verify default parameters - new signature: client, base_url, url_path, params
                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client  # client
                assert call_args[0][1] == mock_braze_context.base_url  # base_url
                assert call_args[0][2] == "campaigns/list"  # url_path
                params = call_args[0][3]  # params
                assert params["page"] == 0
                assert not params["include_archived"]
                assert params["sort_direction"] == "desc"
                assert params["last_edit.time[gt]"] is None

    @pytest.mark.asyncio
    async def test_get_campaign_list_success_with_custom_parameters(
        self, mock_context, mock_braze_context, sample_campaign_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.campaigns.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.campaigns.make_request",
                return_value=SuccessResponse(data=sample_campaign_data, headers={}),
            ) as mock_request:
                await get_campaign_list(
                    mock_context,
                    page=1,
                    include_archived=True,
                    sort_direction="desc",
                    last_edit_time_gt="2025-01-01T00:00:00",
                )

                # Verify parameters were passed correctly
                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client  # client
                assert call_args[0][1] == mock_braze_context.base_url  # base_url
                assert call_args[0][2] == "campaigns/list"  # url_path
                params = call_args[0][3]  # params
                assert params["page"] == 1
                assert params["include_archived"]
                assert params["sort_direction"] == "desc"
                assert params["last_edit.time[gt]"] == "2025-01-01T00:00:00"

    @pytest.mark.asyncio
    async def test_get_campaign_list_request_failure(self, mock_context, mock_braze_context):
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
                result = await get_campaign_list(mock_context)

                assert isinstance(result, dict)
                assert "error" in result
                assert result["error"] == "Request failed"

    @pytest.mark.asyncio
    async def test_get_campaign_list_response_fails_parsing(self, mock_context, mock_braze_context):
        """Test get campaign list returns the raw response when the response fails schema validation"""
        invalid_data = {"message": "success", "campaigns": [{"invalid": "data"}]}
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
                    result = await get_campaign_list(mock_context)

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_campaign_list_unexpected_response_type(
        self, mock_context, mock_braze_context
    ):
        """Test campaign list handles unexpected response type"""

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
                    result = await get_campaign_list(mock_context)

                    assert isinstance(result, dict)
                    assert "error" in result
                    error_obj = result["error"]
                    assert error_obj["error_type"] == "unexpected_error"
                    assert "Unexpected response type:" in error_obj["message"]
                    mock_logger.assert_called_once_with(
                        f"Unexpected response type: {type(unexpected_response)}"
                    )
