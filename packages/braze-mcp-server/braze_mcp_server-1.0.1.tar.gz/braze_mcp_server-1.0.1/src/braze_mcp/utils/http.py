import json
import logging
import re
from dataclasses import dataclass
from logging import Logger
from typing import Any
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

from braze_mcp.models.errors import (
    http_error,
    internal_error,
    parsing_error,
    unexpected_response_error,
)
from braze_mcp.utils.logging import get_logger

logger = get_logger(__name__, log_level=logging.INFO)


@dataclass
class SuccessResponse:
    """Represents a successful response"""

    data: dict[str, Any]
    headers: dict[str, Any]


@dataclass
class FailureResponse:
    """Represents a failed response"""

    data: dict[str, Any]
    error: Exception


def build_http_client(api_key: str, timeout: float = 10.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(headers=build_headers(api_key), timeout=timeout)


def build_headers(api_key: str) -> dict[str, str]:
    if not api_key:
        raise ValueError("api_key must be a non-empty value")
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "X-Braze-MCP-Source": "local-v1.0.0",
    }


def extract_cursor_from_link_header(link_header: str | None) -> str | None:
    """Extract cursor from Link header for pagination

    Args:
        link_header: Link header value like '<https://anna.braze.com/custom_attributes/?cursor=c2tpcDo1MA==>; rel="next"'

    Returns:
        The cursor value or None if not found
    """
    if not link_header:
        return None

    # Parse Link header to find rel="next"
    next_link_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
    if not next_link_match:
        return None

    next_url = next_link_match.group(1)

    # Extract cursor parameter from the URL
    cursor_match = re.search(r"[?&]cursor=([^&]+)", next_url)
    if cursor_match:
        return cursor_match.group(1)

    return None


def _sanitize(data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Filters items that have a value of `None`"""
    if not data:
        return None
    return {k: v for k, v in data.items() if v is not None}


async def make_request(
    client: httpx.AsyncClient,
    base_url: str,
    url_path: str,
    params: dict[str, Any] | None = None,
) -> SuccessResponse | FailureResponse:
    """Make HTTP request with error handling

    Returns:
        SuccessResponse or FailureResponse object
    """
    url = urljoin(base_url, url_path)

    params = _sanitize(params)

    try:
        response = await client.get(url, params=params, timeout=15.0)
        response.raise_for_status()

        response_headers = dict(response.headers)
        json_data = response.json()
        return SuccessResponse(json_data, headers=response_headers)

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON response from {url}"
        logger.exception(error_msg)
        error_data = parsing_error(error_msg, operation=f"request to {url_path}")
        return FailureResponse(error_data, error=e)

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        error_msg = f"Request failed with status code {status_code}"
        logger.exception(error_msg)
        error_data = http_error(
            error_msg,
            status_code=status_code,
            operation=f"request to {url_path}",
        )
        return FailureResponse(error_data, error=e)

    except httpx.HTTPError as e:
        error_msg = "Error occurred while making request"
        logger.exception(error_msg)
        error_data = http_error(error_msg, operation=f"request to {url_path}")
        return FailureResponse(error_data, error=e)

    except Exception as e:
        error_msg = f"Unexpected error in make_request for {url_path}"
        logger.exception(error_msg)
        error_data = internal_error(error_msg, operation=f"request to {url_path}", exception=e)
        return FailureResponse(error_data, error=e)


def handle_response[T: BaseModel](
    response: SuccessResponse | FailureResponse | Any,
    model_class: type[T],
    operation_name: str,
    logger: Logger,
) -> T | dict[str, Any]:
    """Generic helper to handle API responses with consistent error handling and parsing.

    Args:
        response: The HTTP response object (SuccessResponse, FailureResponse, or other)
        model_class: The Pydantic model class to validate the response data
        operation_name: Human-readable name of the operation for logging (e.g., "fetch canvases")
        logger: Logger instance for error reporting

    Returns:
        Parsed model instance on successful parsing, raw data dict on parse failure,
        or error dict on request failure
    """
    match response:
        case SuccessResponse(data=data, headers=_):
            try:
                response_obj = model_class.model_validate(data)
                return response_obj
            except Exception:
                logger.exception(f"Failed to parse {operation_name} response with model")
                return data

        case FailureResponse(data=error_data, error=error):
            logger.error(f"Failed to {operation_name}: {error}")
            return error_data

        case _:
            logger.error(f"Unexpected response type: {type(response)}")
            return unexpected_response_error(str(type(response)), operation=operation_name)
