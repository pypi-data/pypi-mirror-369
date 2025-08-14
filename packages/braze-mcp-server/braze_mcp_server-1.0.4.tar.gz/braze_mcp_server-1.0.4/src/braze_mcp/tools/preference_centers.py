from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import PreferenceCenterDetails, PreferenceCentersResponse
from braze_mcp.utils import get_braze_context, get_logger, make_request
from braze_mcp.utils.http import handle_response

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_preference_centers(ctx: Context) -> PreferenceCentersResponse | dict[str, Any]:
    """Use this endpoint to list your available preference centers.

    Args:
        ctx: The MCP context

    Returns:
        PreferenceCentersResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "preference_center/v1/list"

    # No parameters needed for this endpoint
    params: dict[str, Any] = {}

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, PreferenceCentersResponse, "fetch preference centers", logger)


async def get_preference_center_details(
    ctx: Context, preference_center_id: str
) -> PreferenceCenterDetails | dict[str, Any]:
    """Use this endpoint to view the details for your preference centers, including when it was created and updated.

    Args:
        ctx: The MCP context
        preference_center_id: The ID for your preference center

    Returns:
        PreferenceCenterDetails when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = f"preference_center/v1/{preference_center_id}"

    # No additional parameters needed for this endpoint
    params: dict[str, Any] = {}

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(
        response, PreferenceCenterDetails, "fetch preference center details", logger
    )
