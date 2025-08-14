from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import (
    CustomAttributesResponse,
    CustomAttributesWithPagination,
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
)

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_custom_attributes(
    ctx: Context, cursor: str | None = None
) -> CustomAttributesWithPagination | dict[str, Any]:
    """Use this endpoint to export a list of custom attributes recorded for your app. The attributes are returned in groups of 50, sorted alphabetically.

    Args:
        ctx: The MCP context
        cursor: Optional cursor for pagination to get the next page of results

    Returns:
        CustomAttributesWithPagination when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "custom_attributes"
    params = {"cursor": cursor} if cursor else {}

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    match response:
        case SuccessResponse(data=data, headers=response_headers):
            try:
                parsed_response = CustomAttributesResponse.model_validate(data)

                link_header = response_headers.get("link")
                if link_header:
                    logger.info(f"Found Link header {link_header}")
                next_cursor = extract_cursor_from_link_header(link_header)

                pagination_info = PaginationInfo(
                    current_page_count=len(parsed_response.attributes),
                    has_more_pages=bool(next_cursor),
                    next_cursor=next_cursor,
                    max_per_page=50,
                    link_header=link_header,
                )

                return CustomAttributesWithPagination(
                    message=parsed_response.message,
                    attributes=parsed_response.attributes,
                    pagination_info=pagination_info,
                )
            except Exception:
                logger.exception("Failed to parse custom attributes response with model")
                return data

        case FailureResponse(data=error_data, error=error):
            logger.error(f"Failed to fetch custom attributes: {error}")
            # error_data is already a standardized ErrorResponse from http.py
            return error_data

        case _:
            logger.error(f"Unexpected response type: {type(response)}")
            return unexpected_response_error(str(type(response)), "get_custom_attributes")
