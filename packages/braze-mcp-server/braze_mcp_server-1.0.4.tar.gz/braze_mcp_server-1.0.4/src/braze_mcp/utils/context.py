import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP

from braze_mcp.utils.http import build_http_client
from braze_mcp.utils.logging import get_logger

logger = get_logger(__name__, log_level=logging.INFO)


@dataclass
class BrazeContext:
    """Context for Braze API operations."""

    api_key: str
    base_url: str
    http_client: httpx.AsyncClient


def _get_required_env(key: str) -> str:
    """Get required environment variable or exit with error"""
    env_value = os.environ.get(key)
    if not env_value:
        logger.error(f"{key} environment variable not set")
        raise ValueError(f"{key} environment variable must be set")
    logger.info(f"{key} found")
    return env_value


def _normalize_base_url(url: str) -> str:
    """Normalize base URL by adding https:// if no protocol is specified"""
    if not url:
        return url

    # If URL already has a protocol, return as-is
    if url.startswith(("http://", "https://")):
        return url

    # Add https:// prefix if missing
    normalized_url = f"https://{url}"
    logger.info(f"Normalized URL from '{url}' to '{normalized_url}'")
    return normalized_url


@asynccontextmanager
async def braze_lifespan(server: FastMCP) -> AsyncIterator[BrazeContext]:
    """Initialize and clean up Braze API resources."""
    logger.info("Initializing Braze lifespan...")
    load_dotenv()
    api_key = _get_required_env("BRAZE_API_KEY")
    base_url = _normalize_base_url(_get_required_env("BRAZE_BASE_URL"))
    logger.info(f"Using {base_url} for requests")

    http_client = build_http_client(api_key)
    logger.info("HTTP client created")

    try:
        logger.info("Braze lifespan initialization complete")
        yield BrazeContext(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client,
        )
    finally:
        logger.info("Cleaning up HTTP client")
        await http_client.aclose()


def get_braze_context(ctx: Context) -> BrazeContext:
    """Get the Braze context from the request context."""
    logger.info("Attempting to get Braze context")

    if not ctx:
        logger.error("Context is None")
        raise ValueError("Context is None")

    if not hasattr(ctx, "request_context"):
        logger.error("request_context not found in Context")
        raise ValueError("request_context not found in Context")

    if not hasattr(ctx.request_context, "lifespan_context"):
        logger.error("lifespan_context not found in request_context")
        raise ValueError("lifespan_context not found in request_context")

    logger.info("Successfully retrieved Braze context")
    return ctx.request_context.lifespan_context
