from typing import Any

from mcp.server.fastmcp import Context

from braze_mcp.models import SubscriptionGroupsResponse, SubscriptionGroupStatusResponse
from braze_mcp.utils import get_braze_context, get_logger, make_request
from braze_mcp.utils.http import handle_response

__register_mcp_tools__ = True

logger = get_logger(__name__)


async def get_user_subscription_groups(
    ctx: Context,
    external_id: str | list[str] | None = None,
    email: str | list[str] | None = None,
    phone: str | list[str] | None = None,
    limit: int = 100,
    offset: int = 0,
) -> SubscriptionGroupsResponse | dict[str, Any]:
    """Use this endpoint to list and get the subscription groups of a certain user.

    Args:
        ctx: The MCP context
        external_id: The external_id(s) of the user (must include at least one and at most 50)
        email: The email address(es) of the user (must include at least one and at most 50)
        phone: The phone number(s) of the user in E.164 format (must include at least one and at most 50)
        limit: The limit on the maximum number of results returned (default and maximum is 100)
        offset: Number of templates to skip before returning results

    Returns:
        SubscriptionGroupsResponse when parsing succeeds, otherwise a dictionary containing the raw response data.

    Raises:
        ValueError: If none of external_id, email, or phone are provided, or if both email and phone are provided

    Note:
        API Constraints:
        - At least one identifier (external_id, email, or phone) must be provided
        - Email and phone cannot be used together in the same request
        - External_id can be combined with either email OR phone, but not both
    """
    url_path = "subscription/user/status"

    # Validate that at least one identifier is provided
    if not external_id and not email and not phone:
        raise ValueError("At least one of external_id, email, or phone must be provided")

    # Validate that email and phone are not both provided (API constraint)
    if email and phone:
        raise ValueError(
            "Either an email address or a phone number should be provided, but not both"
        )

    # Build query parameters
    params: dict[str, Any] = {
        "external_id[]": external_id,
        "email[]": email,
        "phone[]": phone,
        "limit": limit,
        "offset": offset,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(
        response, SubscriptionGroupsResponse, "fetch user subscription groups", logger
    )


async def get_subscription_group_status(
    ctx: Context,
    subscription_group_id: str,
    external_id: str | list[str] | None = None,
    email: str | list[str] | None = None,
    phone: str | list[str] | None = None,
) -> SubscriptionGroupStatusResponse | dict[str, Any]:
    """Get the subscription state of a user in a subscription group.

    Args:
        ctx: The MCP context
        subscription_group_id: The id of your subscription group
        external_id: The external_id(s) of the user (must include at least one and at most 50)
        email: The email address(es) of the user (must include at least one and at most 50)
        phone: The phone number(s) of the user in E.164 format (must include at least one and at most 50)

    Returns:
        SubscriptionGroupStatusResponse when parsing succeeds, otherwise a dictionary containing the raw response data.

    Raises:
        ValueError: If none of external_id, email, or phone are provided, or if both email and phone are provided without external_id

    Note:
        API Constraints:
        - subscription_group_id is required
        - For SMS and WhatsApp subscription groups either external_id or phone is required.
            - When both are submitted only the external_iud is used for querying and the phone number is applied to that user
        - For email subscription groups, either external_id or email is required.
            - When both are submitted, only the external_id is used for the query and the email is applied to that user
        - Email and phone cannot be used together without external_id
    """
    url_path = "subscription/status/get"

    # Validate that at least one identifier is provided
    if not external_id:
        if not email and not phone:
            raise ValueError("At least one of external_id, email, or phone must be provided")
        elif email and phone:
            raise ValueError(
                "Either an email address or a phone number should be provided, but not both"
            )

    params: dict[str, Any] = {
        "subscription_group_id": subscription_group_id,
        "external_id[]": external_id,
        "email[]": email,
        "phone[]": phone,
    }

    bctx = get_braze_context(ctx)

    response = await make_request(bctx.http_client, bctx.base_url, url_path, params)

    return handle_response(
        response, SubscriptionGroupStatusResponse, "fetch subscription group status", logger
    )
