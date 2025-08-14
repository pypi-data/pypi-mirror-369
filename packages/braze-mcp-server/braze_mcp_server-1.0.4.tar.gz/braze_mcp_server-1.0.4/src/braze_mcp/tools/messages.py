from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import ScheduledBroadcastsResponse
from braze_mcp.utils import get_braze_context, get_logger, make_request
from braze_mcp.utils.http import handle_response

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_scheduled_broadcasts(
    ctx: Context,
    end_time: str,
) -> ScheduledBroadcastsResponse | dict[str, Any]:
    """Use this endpoint to return a JSON list of information about scheduled campaigns and entry Canvases between now and a designated end_time.

    Daily, recurring messages will only appear once with their next occurrence. Results returned
    in this endpoint include campaigns and Canvases created and scheduled in the Braze dashboard.

    Args:
        ctx: The MCP context
        end_time: End date of the range to retrieve upcoming scheduled campaigns and Canvases.
                 This is treated as midnight in UTC time by the API. Format: ISO-8601
                 (e.g., "2018-09-01T00:00:00-04:00")

    Returns:
        ScheduledBroadcastsResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "messages/scheduled_broadcasts"

    params = {
        "end_time": end_time,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(
        response, ScheduledBroadcastsResponse, "fetch scheduled broadcasts", logger
    )
