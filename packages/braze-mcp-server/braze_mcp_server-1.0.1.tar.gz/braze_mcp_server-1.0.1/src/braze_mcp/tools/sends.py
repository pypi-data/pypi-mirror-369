from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import SendDataSeriesResponse
from braze_mcp.utils import get_braze_context, get_logger, make_request
from braze_mcp.utils.http import (
    handle_response,
)

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_send_data_series(
    ctx: Context,
    campaign_id: str,
    send_id: str,
    length: int,
    ending_at: str | None = None,
) -> SendDataSeriesResponse | dict[str, Any]:
    """Use this endpoint to retrieve a daily series of various stats for a tracked send_id for API campaigns.

    Braze stores send analytics for 14 days after the send. Campaign conversions will be attributed toward
    the most recent send_id that a given user has received from the campaign.

    Args:
        ctx: The MCP context
        campaign_id: The campaign_id for API campaigns can be found on the API Keys page and the Campaign Details page within your dashboard; or you can use the Export campaigns list endpoint.
        send_id: The Send API identifier for the specific send
        length: Maximum number of days before ending_at to include in the returned series. Must be between 1 and 100 (inclusive).
        ending_at: Date on which the data series should end (format: ISO-8601 datetime string). Defaults to time of the request.

    Returns:
        SendDataSeriesResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "sends/data_series"

    params = {
        "campaign_id": campaign_id,
        "send_id": send_id,
        "length": length,
        "ending_at": ending_at,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, SendDataSeriesResponse, "fetch send data series", logger)
