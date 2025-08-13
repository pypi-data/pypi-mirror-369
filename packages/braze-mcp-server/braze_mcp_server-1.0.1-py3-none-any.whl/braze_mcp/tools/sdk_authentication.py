from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import SDKAuthenticationKeysResponse
from braze_mcp.utils import get_braze_context, get_logger, make_request
from braze_mcp.utils.http import handle_response

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_sdk_authentication_keys(
    ctx: Context,
    app_id: str,
) -> SDKAuthenticationKeysResponse | dict[str, Any]:
    """Use this endpoint to retrieve all SDK Authentication keys for your app.

    Args:
        ctx: The MCP context
        app_id: The app API identifier

    Returns:
        SDKAuthenticationKeysResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "app_group/sdk_authentication/keys"

    params = {
        "app_id": app_id,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(
        response, SDKAuthenticationKeysResponse, "fetch SDK authentication keys", logger
    )
