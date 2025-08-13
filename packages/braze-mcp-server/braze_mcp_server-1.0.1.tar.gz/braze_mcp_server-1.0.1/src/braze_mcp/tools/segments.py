from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import (
    SegmentDataSeriesResponse,
    SegmentDetails,
    SegmentListResponse,
)
from braze_mcp.utils import get_braze_context, get_logger, make_request
from braze_mcp.utils.http import (
    handle_response,
)

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_segment_list(
    ctx: Context,
    page: int = 0,
    sort_direction: str = "desc",
) -> SegmentListResponse | dict[str, Any]:
    """Use this endpoint to export a list of segments, each of which will include its name, Segment API identifier, and whether it has analytics tracking enabled.

    Args:
        ctx: The MCP context
        page: The page of segments to return, defaults to 0 (returns the first set of up to 100)
        sort_direction: Sort creation time from newest to oldest: pass in the value desc. Sort creation time from oldest to newest: pass in the value asc. If sort_direction is not included, the default order is oldest to newest

    Returns:
        SegmentListResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "segments/list"

    params = {
        "page": page,
        "sort_direction": sort_direction,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, SegmentListResponse, "fetch segment list", logger)


async def get_segment_data_series(
    ctx: Context,
    segment_id: str,
    length: int,
    ending_at: str | None = None,
) -> SegmentDataSeriesResponse | dict[str, Any]:
    """Use this endpoint to retrieve a daily series of the estimated size of a segment over time.

    Args:
        ctx: The MCP context
        segment_id: Segment API identifier. The segment_id for a given segment can be found on the API Keys page within your Braze account or you can use the Export segment list endpoint
        length: Maximum number of days before ending_at to include in the returned series. Must be between 1 and 100 (inclusive)
        ending_at: Date on which the data series should end (ISO-8601 string). Defaults to time of the request

    Returns:
        SegmentDataSeriesResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "segments/data_series"

    params = {
        "segment_id": segment_id,
        "length": length,
        "ending_at": ending_at,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, SegmentDataSeriesResponse, "fetch segment data series", logger)


async def get_segment_details(ctx: Context, segment_id: str) -> SegmentDetails | dict[str, Any]:
    """Use this endpoint to retrieve relevant information on a segment, which can be identified by the segment_id.

    Args:
        ctx: The MCP context
        segment_id: Segment API identifier. The segment_id for a given segment can be found on the API Keys page within your Braze account or you can use the Export segment list endpoint

    Returns:
        SegmentDetails when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "segments/details"

    params = {
        "segment_id": segment_id,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, SegmentDetails, "fetch segment details", logger)
