from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import SessionDataSeriesResponse
from braze_mcp.utils import get_braze_context, get_logger, make_request
from braze_mcp.utils.http import (
    handle_response,
)

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_session_data_series(
    ctx: Context,
    length: int,
    unit: str | None = None,
    ending_at: str | None = None,
    app_id: str | None = None,
    segment_id: str | None = None,
) -> SessionDataSeriesResponse | dict[str, Any]:
    """Use this endpoint to retrieve a series of the number of sessions for your app over a designated time period.

    Args:
        ctx: The MCP context
        length: Maximum number of units (days or hours) before ending_at to include in the returned series. Must be between 1 and 100 (inclusive)
        unit: Unit of time between data points. Can be day or hour, defaults to day
        ending_at: Date on which the data series should end (ISO-8601 string). Defaults to time of the request
        app_id: App API identifier retrieved from the API Keys page to limit analytics to a specific app
        segment_id: Segment API identifier. Segment ID indicating the analytics-enabled segment for which sessions should be returned

    Returns:
        SessionDataSeriesResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "sessions/data_series"

    params = {
        "length": length,
        "unit": unit,
        "ending_at": ending_at,
        "app_id": app_id,
        "segment_id": segment_id,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, SessionDataSeriesResponse, "fetch session data series", logger)
