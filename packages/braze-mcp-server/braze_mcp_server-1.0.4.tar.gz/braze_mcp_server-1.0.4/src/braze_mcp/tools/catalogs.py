from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import (
    CatalogItemsResponse,
    CatalogItemsWithPagination,
    CatalogsResponse,
    PaginationInfo,
)
from braze_mcp.models.errors import unexpected_response_error
from braze_mcp.utils import (
    extract_cursor_from_link_header,
    get_braze_context,
    get_logger,
    make_request,
)
from braze_mcp.utils.http import FailureResponse, SuccessResponse, handle_response

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_catalogs(ctx: Context) -> CatalogsResponse | dict[str, Any]:
    """Use this endpoint to return a list of catalogs in a workspace.

    Parameters:
        ctx: The MCP context

    Returns:
        CatalogsResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "catalogs"

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path)

    return handle_response(response, CatalogsResponse, "fetch catalogs", logger)


async def get_catalog_items(
    ctx: Context, catalog_name: str, cursor: str | None = None
) -> CatalogItemsWithPagination | dict[str, Any]:
    """Use this endpoint to return multiple catalog items and their content.

    Parameters:
        ctx: The MCP context
        catalog_name: Name of the catalog
        cursor: Optional cursor for pagination to get the next page of results

    Returns:
        CatalogItemsWithPagination when parsing succeeds, otherwise a dictionary containing the raw response data.

    Note:
        - Each call returns 50 items. For catalogs with more than 50 items, use the Link header for pagination
    """
    url_path = f"catalogs/{catalog_name}/items"
    params = {"cursor": cursor} if cursor else {}

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    match response:
        case SuccessResponse(data=data, headers=response_headers):
            try:
                parsed_response = CatalogItemsResponse.model_validate(data)

                link_header = response_headers.get("link")
                if link_header:
                    logger.info(f"Found Link header {link_header}")
                next_cursor = extract_cursor_from_link_header(link_header)

                pagination_info = PaginationInfo(
                    current_page_count=len(parsed_response.items),
                    has_more_pages=bool(next_cursor),
                    next_cursor=next_cursor,
                    max_per_page=50,
                    link_header=link_header,
                )

                return CatalogItemsWithPagination(
                    message=parsed_response.message,
                    items=parsed_response.items,
                    pagination_info=pagination_info,
                )
            except Exception:
                logger.exception("Failed to parse catalog items response with model")
                return data

        case FailureResponse(data=error_data, error=error):
            logger.error(f"Failed to fetch catalog items: {error}")
            # error_data is already a standardized ErrorResponse from http.py
            return error_data

        case _:
            logger.error(f"Unexpected response type: {type(response)}")
            return unexpected_response_error(str(type(response)), "get_catalog_items")


async def get_catalog_item(
    ctx: Context, catalog_name: str, item_id: str
) -> CatalogItemsResponse | dict[str, Any]:
    """Use this endpoint to return a catalog item and its content.

    Parameters:
        ctx: The MCP context
        catalog_name: Name of the catalog
        item_id: The ID of the catalog item

    Returns:
        CatalogItemsResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = f"catalogs/{catalog_name}/items/{item_id}"

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path)

    return handle_response(response, CatalogItemsResponse, "fetch catalog item", logger)
