from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import (
    ProductListResponse,
    QuantitySeriesResponse,
    RevenueSeriesResponse,
)
from braze_mcp.utils import get_braze_context, get_logger, make_request
from braze_mcp.utils.http import (
    handle_response,
)

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_product_list(
    ctx: Context, page: str | None = None
) -> ProductListResponse | dict[str, Any]:
    """Use this endpoint to return a paginated lists of product IDs.

    Args:
        ctx: The MCP context
        page: The page of your product list that you want to view

    Returns:
        ProductListResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "purchases/product_list"

    params = {
        "page": page,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, ProductListResponse, "fetch product list", logger)


async def get_revenue_series(
    ctx: Context,
    length: int,
    ending_at: str | None = None,
    unit: str | None = None,
    app_id: str | None = None,
    product: str | None = None,
) -> RevenueSeriesResponse | dict[str, Any]:
    """Use this endpoint to return the total money spent in your app over a time range.

    Args:
        ctx: The MCP context
        length: Maximum number of days before ending_at to include in the returned series. Must be between 1 and 100 (inclusive)
        ending_at: Date on which the data export should end (ISO-8601 string). Defaults to time of the request
        unit: Unit of time between data points. Can be day or hour, defaults to day
        app_id: App API identifier retrieved from the API Keys page. If excluded, results for all apps in a workspace will be returned
        product: Name of product to filter response by. If excluded, results for all apps will be returned

    Returns:
        RevenueSeriesResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "purchases/revenue_series"

    params = {
        "length": length,
        "ending_at": ending_at,
        "unit": unit,
        "app_id": app_id,
        "product": product,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, RevenueSeriesResponse, "fetch revenue series", logger)


async def get_quantity_series(
    ctx: Context,
    length: int,
    ending_at: str | None = None,
    unit: str | None = None,
    app_id: str | None = None,
    product: str | None = None,
) -> QuantitySeriesResponse | dict[str, Any]:
    """Use this endpoint to return the total number of purchases in your app over a time range.

    Args:
        ctx: The MCP context
        length: Maximum number of days before ending_at to include in the returned series. Must be between 1 and 100 (inclusive)
        ending_at: Date on which the data export should end (ISO-8601 string). Defaults to time of the request
        unit: Unit of time between data points. Can be day or hour, defaults to day
        app_id: App API identifier retrieved from the API Keys page. If excluded, results for all apps in a workspace will be returned
        product: Name of product to filter response by. If excluded, results for all apps will be returned

    Returns:
        QuantitySeriesResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "purchases/quantity_series"

    params = {
        "length": length,
        "ending_at": ending_at,
        "unit": unit,
        "app_id": app_id,
        "product": product,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, QuantitySeriesResponse, "fetch quantity series", logger)
