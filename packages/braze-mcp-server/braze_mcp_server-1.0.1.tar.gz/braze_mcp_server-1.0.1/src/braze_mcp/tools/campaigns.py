from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import (
    CampaignDataSeriesResponse,
    CampaignDetails,
    CampaignListResponse,
)
from braze_mcp.utils import get_braze_context, get_logger, make_request
from braze_mcp.utils.http import (
    handle_response,
)

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_campaign_list(
    ctx: Context,
    page: int = 0,
    include_archived: bool = False,
    sort_direction: str = "desc",
    last_edit_time_gt: str | None = None,
) -> CampaignListResponse | dict[str, Any]:
    """Use this endpoint to export a list of campaigns, each of which will include its name,
    campaign API identifier, whether it is an API campaign, and tags associated with the campaign.

    Args:
        ctx: The MCP context
        page: Represents the page of campaigns to return, defaults to 0 (returns the first set of up to 100)
        include_archived: Whether to include archived campaigns, defaults to false
        sort_direction: Sort creation time - 'desc' for newest to oldest, 'asc' for oldest to newest
        last_edit_time_gt: Filters results to campaigns edited after this time (format: yyyy-MM-DDTHH:mm:ss)

    Returns:
        CampaignListResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "campaigns/list"

    params = {
        "page": page,
        "include_archived": include_archived,
        "sort_direction": sort_direction,
        "last_edit.time[gt]": last_edit_time_gt,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, CampaignListResponse, "fetch campaigns", logger)


async def get_campaign_details(
    ctx: Context, campaign_id: str, post_launch_draft_version: bool = False
) -> CampaignDetails | dict[str, Any]:
    """Use this endpoint to retrieve relevant information on a specified campaign, which can be identified by the campaign_id.

    Args:
        ctx: The MCP context
        campaign_id: The campaign_id for API campaigns can be found on the API Keys page and the Campaign Details page within your dashboard; or you can use the Export campaigns list endpoint.
        post_launch_draft_version: For messages that have a post-launch draft, setting this to true will show any draft changes available. Defaults to false

    Returns:
        CampaignDetails when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "campaigns/details"

    params = {
        "campaign_id": campaign_id,
        "post_launch_draft_version": post_launch_draft_version,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, CampaignDetails, "fetch campaign details", logger)


async def get_campaign_dataseries(
    ctx: Context,
    campaign_id: str,
    length: int,
    ending_at: str | None = None,
) -> CampaignDataSeriesResponse | dict[str, Any]:
    """Use this endpoint to retrieve a daily series of various stats for a campaign over time.

    Data returned includes how many messages were sent, opened, clicked, or converted by messaging channel.

    Args:
        ctx: The MCP context
        campaign_id: The campaign_id for API campaigns can be found on the API Keys page and the Campaign Details page within your dashboard; or you can use the Export campaigns list endpoint.
        length: Maximum number of days before ending_at to include in the returned series. Must be between 1 and 100 (inclusive).
        ending_at: Date on which the data series should end (format: ISO-8601 datetime string). Defaults to time of the request.

    Returns:
        CampaignDataSeriesResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "campaigns/data_series"

    params = {
        "campaign_id": campaign_id,
        "length": length,
        "ending_at": ending_at,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(
        response, CampaignDataSeriesResponse, "fetch campaign dataseries", logger
    )
