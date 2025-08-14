from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models.canvas_dataseries import CanvasDataSeriesResponse
from braze_mcp.models.canvases import (
    CanvasDataSummaryResponse,
    CanvasDetails,
    CanvasListResponse,
)
from braze_mcp.models.errors import validation_error
from braze_mcp.utils import get_braze_context, get_logger, make_request
from braze_mcp.utils.http import (
    handle_response,
)

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_canvas_list(
    ctx: Context,
    page: int = 0,
    include_archived: bool = False,
    sort_direction: str = "desc",
    last_edit_time_gt: str | None = None,
) -> CanvasListResponse | dict[str, Any]:
    """Use this endpoint to export a list of Canvases, each of which will include its name,
    Canvas API identifier, and tags associated with the Canvas.

    Args:
        ctx: The MCP context
        page: Represents the page of Canvases to return, defaults to 0 (returns the first set of up to 100)
        include_archived: Whether to include archived Canvases, defaults to false
        sort_direction: Sort creation time - 'desc' for newest to oldest, 'asc' for oldest to newest
        last_edit_time_gt: Filters results to Canvases edited after this time (format: yyyy-MM-DDTHH:mm:ss)

    Returns:
        CanvasListResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "canvas/list"

    params = {
        "page": page,
        "include_archived": include_archived,
        "sort_direction": sort_direction,
        "last_edit.time[gt]": last_edit_time_gt,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, CanvasListResponse, "fetch canvases", logger)


async def get_canvas_details(
    ctx: Context, canvas_id: str, post_launch_draft_version: bool = False
) -> CanvasDetails | dict[str, Any]:
    """Use this endpoint to export metadata about a Canvas, such as the name, time created, current status, and more.

    Args:
        ctx: The MCP context
        canvas_id: The Canvas API identifier - can be found on the API Keys page and the Canvas Details page within your dashboard; or you can use the Export canvases list endpoint.
        post_launch_draft_version: For Canvases that have a post-launch draft, setting this to true will show any draft changes available. Defaults to false

    Returns:
        CanvasDetails when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "canvas/details"

    params = {
        "canvas_id": canvas_id,
        "post_launch_draft_version": post_launch_draft_version,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, CanvasDetails, "fetch canvas details", logger)


async def get_canvas_data_summary(
    ctx: Context,
    canvas_id: str,
    ending_at: str,
    starting_at: str | None = None,
    length: int | None = None,
    include_variant_breakdown: bool = False,
    include_step_breakdown: bool = False,
    include_deleted_step_data: bool = False,
) -> CanvasDataSummaryResponse | dict[str, Any]:
    """Use this endpoint to export rollups of time series data for a Canvas, providing a concise summary of Canvas results.

    Args:
        ctx: The MCP context
        canvas_id: The Canvas API identifier - can be found on the API Keys page and the Canvas Details page within your dashboard; or you can use the Export canvases list endpoint.
        ending_at: Date on which the data export should end (ISO-8601 datetime string). Defaults to time of the request.
        starting_at: Date on which the data export should begin (ISO-8601 datetime string). Either length or starting_at is required.
        length: Maximum number of days before ending_at to include in the returned series. Must be between 1 and 14 (inclusive). Either length or starting_at is required.
        include_variant_breakdown: Whether to include variant statistics (defaults to false).
        include_step_breakdown: Whether to include step statistics (defaults to false).
        include_deleted_step_data: Whether to include step statistics for deleted steps (defaults to false).

    Returns:
        CanvasDataSummaryResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    # Validate that either starting_at or length is provided
    if starting_at is None and length is None:
        return validation_error(
            "Either starting_at or length parameter is required", "get_canvas_data_summary"
        )

    url_path = "canvas/data_summary"

    params = {
        "canvas_id": canvas_id,
        "ending_at": ending_at,
        "starting_at": starting_at,
        "length": length,
        "include_variant_breakdown": include_variant_breakdown,
        "include_step_breakdown": include_step_breakdown,
        "include_deleted_step_data": include_deleted_step_data,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, CanvasDataSummaryResponse, "fetch canvas data summary", logger)


async def get_canvas_data_series(
    ctx: Context,
    canvas_id: str,
    ending_at: str,
    starting_at: str | None = None,
    length: int | None = None,
    include_variant_breakdown: bool = False,
    include_step_breakdown: bool = False,
    include_deleted_step_data: bool = False,
) -> CanvasDataSeriesResponse | dict[str, Any]:
    """Use this endpoint to export time series data for a Canvas.

    Args:
        ctx: The MCP context
        canvas_id: The Canvas API identifier - can be found on the API Keys page and the Canvas Details page within your dashboard; or you can use the Export canvases list endpoint.
        ending_at: Date on which the data export should end (ISO-8601 datetime string). Defaults to time of the request.
        starting_at: Date on which the data export should begin (ISO-8601 datetime string). Either length or starting_at is required.
        length: Maximum number of days before ending_at to include in the returned series. Must be between 1 and 14 (inclusive). Either length or starting_at is required.
        include_variant_breakdown: Whether to include variant statistics (defaults to false).
        include_step_breakdown: Whether to include step statistics (defaults to false).
        include_deleted_step_data: Whether to include step statistics for deleted steps (defaults to false).

    Returns:
        CanvasDataSeriesResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    # Validate that either starting_at or length is provided
    if starting_at is None and length is None:
        return validation_error(
            "Either starting_at or length parameter is required", operation="get_canvas_data_series"
        )

    url_path = "canvas/data_series"

    params = {
        "canvas_id": canvas_id,
        "ending_at": ending_at,
        "starting_at": starting_at,
        "length": length,
        "include_variant_breakdown": include_variant_breakdown,
        "include_step_breakdown": include_step_breakdown,
        "include_deleted_step_data": include_deleted_step_data,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, CanvasDataSeriesResponse, "fetch canvas data series", logger)
