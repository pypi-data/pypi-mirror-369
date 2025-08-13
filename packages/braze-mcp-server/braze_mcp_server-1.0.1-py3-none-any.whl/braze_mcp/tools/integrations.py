from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import (
    IntegrationsListResponse,
    JobSyncStatusResponse,
)
from braze_mcp.utils import get_braze_context, get_logger, make_request
from braze_mcp.utils.http import (
    handle_response,
)

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def list_integrations(
    ctx: Context,
    cursor: str | None = None,
) -> IntegrationsListResponse | dict[str, Any]:
    """Use this endpoint to return a list of existing CDI integrations.

    Each call returns 10 items. For lists with more than 10 integrations, use the Link header
    to retrieve data on the next page.

    Args:
        ctx: The MCP context
        cursor: Determines the pagination of the integration list

    Returns:
        IntegrationsListResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "cdi/integrations"

    params = {}
    if cursor:
        params["cursor"] = cursor

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, IntegrationsListResponse, "fetch CDI integrations", logger)


async def get_integration_job_sync_status(
    ctx: Context,
    integration_id: str,
    cursor: str | None = None,
) -> JobSyncStatusResponse | dict[str, Any]:
    """Use this endpoint to return a list of past sync statuses for a given CDI integration.

    Each call returns 10 items. For integrations with more than 10 syncs, use the Link header
    to retrieve data on the next page.

    Args:
        ctx: The MCP context
        integration_id: Integration ID
        cursor: Determines the pagination of the sync status

    Returns:
        JobSyncStatusResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = f"cdi/integrations/{integration_id}/job_sync_status"

    params = {}
    if cursor:
        params["cursor"] = cursor

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(
        response, JobSyncStatusResponse, "fetch CDI integration job sync status", logger
    )
