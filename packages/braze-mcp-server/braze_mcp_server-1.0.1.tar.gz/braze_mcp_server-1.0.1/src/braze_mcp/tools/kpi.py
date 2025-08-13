from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import (
    DAUDataSeriesResponse,
    MAUDataSeriesResponse,
    NewUsersDataSeriesResponse,
    UninstallsDataSeriesResponse,
)
from braze_mcp.utils import get_braze_context, get_logger, make_request
from braze_mcp.utils.http import (
    handle_response,
)

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_new_users_data_series(
    ctx: Context,
    length: int,
    ending_at: str | None = None,
    app_id: str | None = None,
) -> NewUsersDataSeriesResponse | dict[str, Any]:
    """Use this endpoint to retrieve a daily series of the total number of new users on each date.

    Args:
        ctx: The MCP context
        length: Maximum number of days before ending_at to include in the returned series. Must be between 1 and 100 (inclusive)
        ending_at: Date on which the data series should end (ISO-8601 string). Defaults to time of the request
        app_id: App API identifier retrieved from the API Keys page. If excluded, results for all apps in workspace will be returned

    Returns:
        NewUsersDataSeriesResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "kpi/new_users/data_series"

    params = {
        "length": length,
        "ending_at": ending_at,
        "app_id": app_id,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(
        response, NewUsersDataSeriesResponse, "fetch new users data series", logger
    )


async def get_dau_data_series(
    ctx: Context,
    length: int,
    ending_at: str | None = None,
    app_id: str | None = None,
) -> DAUDataSeriesResponse | dict[str, Any]:
    """Use this endpoint to retrieve a daily series of the total number of unique active users on each date.

    Args:
        ctx: The MCP context
        length: Maximum number of days before ending_at to include in the returned series. Must be between 1 and 100 (inclusive)
        ending_at: Date on which the data series should end (ISO-8601 string). Defaults to time of the request
        app_id: App API identifier retrieved from the API Keys page. If excluded, results for all apps in workspace will be returned

    Returns:
        DAUDataSeriesResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "kpi/dau/data_series"

    params = {
        "length": length,
        "ending_at": ending_at,
        "app_id": app_id,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, DAUDataSeriesResponse, "fetch DAU data series", logger)


async def get_mau_data_series(
    ctx: Context,
    length: int,
    ending_at: str | None = None,
    app_id: str | None = None,
) -> MAUDataSeriesResponse | dict[str, Any]:
    """Use this endpoint to retrieve a daily series of the total number of unique active users over a 30-day rolling window.

    Args:
        ctx: The MCP context
        length: Maximum number of days before ending_at to include in the returned series. Must be between 1 and 100 (inclusive)
        ending_at: Date on which the data series should end (ISO-8601 string). Defaults to time of the request
        app_id: App API identifier retrieved from the API Keys page. If excluded, results for all apps in workspace will be returned

    Returns:
        MAUDataSeriesResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "kpi/mau/data_series"

    params = {
        "length": length,
        "ending_at": ending_at,
        "app_id": app_id,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, MAUDataSeriesResponse, "fetch MAU data series", logger)


async def get_uninstalls_data_series(
    ctx: Context,
    length: int,
    ending_at: str | None = None,
    app_id: str | None = None,
) -> UninstallsDataSeriesResponse | dict[str, Any]:
    """Use this endpoint to retrieve a daily series of the total number of uninstalls on each date.

    Args:
        ctx: The MCP context
        length: Maximum number of days before ending_at to include in the returned series. Must be between 1 and 100 (inclusive)
        ending_at: Date on which the data series should end (ISO-8601 string). Defaults to time of the request
        app_id: App API identifier retrieved from the API Keys page. If excluded, results for all apps in workspace will be returned

    Returns:
        UninstallsDataSeriesResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "kpi/uninstalls/data_series"

    params = {
        "length": length,
        "ending_at": ending_at,
        "app_id": app_id,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(
        response, UninstallsDataSeriesResponse, "fetch uninstalls data series", logger
    )
