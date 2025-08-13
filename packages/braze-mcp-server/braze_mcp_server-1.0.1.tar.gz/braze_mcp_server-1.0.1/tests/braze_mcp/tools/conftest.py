"""Shared test fixtures for Braze MCP tools tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from braze_mcp.utils.context import BrazeContext


@pytest.fixture
def mock_context():
    """Create a mock MCP context with embedded BrazeContext."""
    mock_ctx = MagicMock()
    mock_ctx.request_context = MagicMock()
    mock_ctx.request_context.lifespan_context = BrazeContext(
        api_key="test_api_key",
        base_url="https://test.braze.com",
        http_client=AsyncMock(),
    )
    return mock_ctx


@pytest.fixture
def mock_braze_context():
    """Create a mock BrazeContext for testing."""
    return BrazeContext(
        api_key="test_api_key",
        base_url="https://test.braze.com",
        http_client=AsyncMock(),
    )
