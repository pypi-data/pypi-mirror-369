from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import (
    EventDataSeriesResponse,
    EventListResponse,
    EventsResponse,
    EventsWithPagination,
    PaginationInfo,
)
from braze_mcp.models.errors import unexpected_response_error
from braze_mcp.utils import (
    extract_cursor_from_link_header,
    get_braze_context,
    get_logger,
    make_request,
)
from braze_mcp.utils.http import (
    FailureResponse,
    SuccessResponse,
    handle_response,
)

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_events_list(
    ctx: Context,
    page: int = 0,
) -> EventListResponse | dict[str, Any]:
    """Use this endpoint to export a list of custom events that have been recorded for your app.
    The event names are returned in groups of 250, sorted alphabetically.

    Args:
        ctx: The MCP context
        page: The page of event names to return, defaults to 0 (returns the first set of up to 250)

    Returns:
        EventListResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "events/list"

    params = {
        "page": page,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, EventListResponse, "fetch events list", logger)


async def get_events_data_series(
    ctx: Context,
    event: str,
    length: int,
    unit: str = "day",
    ending_at: str | None = None,
    app_id: str | None = None,
    segment_id: str | None = None,
) -> EventDataSeriesResponse | dict[str, Any]:
    """Use this endpoint to retrieve a series of the number of occurrences of a custom event
    in your app over a designated time period.

    Args:
        ctx: The MCP context
        event: The name of the custom event for which to return analytics
        length: Maximum number of units (days or hours) before ending_at to include in the returned series. Must be between 1 and 100 (inclusive)
        unit: Unit of time between data points. Can be day or hour, defaults to day
        ending_at: Date on which the data series should end (ISO-8601 string). Defaults to time of the request
        app_id: App API identifier retrieved from the API Keys page to limit analytics to a specific app
        segment_id: Segment API identifier. Segment ID indicating the analytics-enabled segment for which event analytics should be returned

    Returns:
        EventDataSeriesResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "events/data_series"

    params = {
        "event": event,
        "length": length,
        "unit": unit,
        "ending_at": ending_at,
        "app_id": app_id,
        "segment_id": segment_id,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, EventDataSeriesResponse, "fetch events data series", logger)


async def get_events(
    ctx: Context,
    cursor: str | None = None,
) -> EventsWithPagination | dict[str, Any]:
    """Use this endpoint to export a list of custom events recorded for your app.
    The events are returned in groups of 50, sorted alphabetically.

    Args:
        ctx: The MCP context
        cursor: Determines the pagination of the custom events

    Returns:
        EventsWithPagination when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "events"
    params = {"cursor": cursor} if cursor else {}

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    match response:
        case SuccessResponse(data=data, headers=response_headers):
            try:
                parsed_response = EventsResponse.model_validate(data)

                link_header = response_headers.get("link")
                if link_header:
                    logger.info(f"Found Link header {link_header}")
                next_cursor = extract_cursor_from_link_header(link_header)

                pagination_info = PaginationInfo(
                    current_page_count=len(parsed_response.events),
                    has_more_pages=bool(next_cursor),
                    next_cursor=next_cursor,
                    max_per_page=50,
                    link_header=link_header,
                )

                return EventsWithPagination(
                    message=parsed_response.message,
                    events=parsed_response.events,
                    pagination_info=pagination_info,
                )
            except Exception:
                logger.exception("Failed to parse events response with model")
                return data

        case FailureResponse(data=error_data, error=error):
            logger.error(f"Failed to fetch events: {error}")
            # error_data is already a standardized ErrorResponse from http.py
            return error_data

        case _:
            logger.error(f"Unexpected response type: {type(response)}")
            return unexpected_response_error(str(type(response)), "get_events")
