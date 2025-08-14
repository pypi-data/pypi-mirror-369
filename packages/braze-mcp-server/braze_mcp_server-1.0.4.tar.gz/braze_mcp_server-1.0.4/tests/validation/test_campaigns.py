"""Real API validation tests for campaigns tools."""

import pytest

from braze_mcp.models.campaigns import CampaignListResponse
from braze_mcp.tools.campaigns import get_campaign_list


@pytest.mark.real_api
class TestCampaignsRealAPI:
    """Real API tests for campaigns tools."""

    @pytest.mark.asyncio
    async def test_get_campaign_list_basic(self, real_context):
        """Test get_campaign_list against real Braze API."""
        result = await get_campaign_list(real_context)

        # Validate return type is Pydantic model
        assert isinstance(result, CampaignListResponse), (
            f"Expected CampaignListResponse, got {type(result)}"
        )

        # Validate response structure
        assert hasattr(result, "campaigns"), "Response should have campaigns attribute"
        assert hasattr(result, "message"), "Response should have message attribute"

        # Validate data types
        assert isinstance(result.campaigns, list), "Campaigns should be a list"
        assert isinstance(result.message, str), "Message should be a string"

        # If campaigns exist, validate structure
        if result.campaigns:
            campaign = result.campaigns[0]
            assert hasattr(campaign, "id"), "Campaign should have id attribute"
            assert hasattr(campaign, "name"), "Campaign should have name attribute"
            assert hasattr(campaign, "last_edited"), "Campaign should have last_edited attribute"

    @pytest.mark.asyncio
    async def test_get_campaign_list_with_parameters(self, real_context):
        """Test get_campaign_list with parameters against real Braze API."""
        result = await get_campaign_list(
            real_context, page=0, include_archived=False, sort_direction="desc"
        )

        # Validate return type is Pydantic model
        assert isinstance(result, CampaignListResponse), (
            f"Expected CampaignListResponse, got {type(result)}"
        )

        # Should still get valid response
        assert hasattr(result, "campaigns"), "Response should have campaigns attribute"
        assert hasattr(result, "message"), "Response should have message attribute"
