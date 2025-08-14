from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import (
    ContentBlockInfo,
    ContentBlocksResponse,
    EmailTemplateInfo,
    EmailTemplatesResponse,
)
from braze_mcp.utils import get_braze_context, get_logger, make_request
from braze_mcp.utils.http import handle_response

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_content_blocks(
    ctx: Context,
    modified_after: str | None = None,
    modified_before: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> ContentBlocksResponse | dict[str, Any]:
    """Use this endpoint to list your existing Content Blocks information.

    Parameters:
        ctx: The MCP context
        modified_after: Retrieve only Content Blocks updated at or after the given time (ISO-8601 format)
        modified_before: Retrieve only Content Blocks updated at or before the given time (ISO-8601 format)
        limit: Maximum number of Content Blocks to retrieve (default 100, max 1000)
        offset: Number of Content Blocks to skip before returning results

    Returns:
        ContentBlocksResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "content_blocks/list"

    # Build query parameters
    params = {
        "modified_after": modified_after,
        "modified_before": modified_before,
        "limit": limit,
        "offset": offset,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, ContentBlocksResponse, "fetch content blocks", logger)


async def get_content_block_info(
    ctx: Context,
    content_block_id: str,
    include_inclusion_data: bool = False,
) -> ContentBlockInfo | dict[str, Any]:
    """Use this endpoint to call information for your existing Content Blocks.

    Parameters:
        ctx: The MCP context
        content_block_id: The Content Block identifier
        include_inclusion_data: When set to true, the API returns back the Message Variation API identifier of campaigns and Canvases where this Content Block is included, to be used in subsequent calls. The results exclude archived or deleted campaigns or Canvases.

    Returns:
        ContentBlockInfo when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "content_blocks/info"

    params = {
        "content_block_id": content_block_id,
        "include_inclusion_data": include_inclusion_data,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, ContentBlockInfo, "fetch content block info", logger)


async def get_email_templates(
    ctx: Context,
    modified_after: str | None = None,
    modified_before: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> EmailTemplatesResponse | dict[str, Any]:
    """Use this endpoint to get a list of available email templates in your Braze account.

    Args:
        ctx: The MCP context
        modified_after: Retrieve only templates updated at or after the given time (ISO-8601 format)
        modified_before: Retrieve only templates updated at or before the given time (ISO-8601 format)
        limit: Maximum number of templates to retrieve (default 100, max 1000)
        offset: Number of templates to skip before returning results

    Returns:
        EmailTemplatesResponse when parsing succeeds, otherwise a dictionary containing the raw response data.
    """
    url_path = "templates/email/list"

    # Build query parameters
    params = {
        "modified_after": modified_after,
        "modified_before": modified_before,
        "limit": limit,
        "offset": offset,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, EmailTemplatesResponse, "fetch email templates", logger)


async def get_email_template_info(
    ctx: Context,
    email_template_id: str,
) -> EmailTemplateInfo | dict[str, Any]:
    """Use this endpoint to get information for a specific email template.
    Note: Templates built using the drag-and-drop editor for email are not accepted.

    Args:
        ctx: The MCP context containing request information
        email_template_id: Your email template's API Identifier

    Returns:
        EmailTemplateInfo: The detailed email template information, or error dict if failed
    """
    url_path = "templates/email/info"

    # Build query parameters
    params = {
        "email_template_id": email_template_id,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(response, EmailTemplateInfo, "fetch email template info", logger)
