"""Shared fixtures for real API validation tests."""

import os
from unittest.mock import MagicMock

import pytest

from braze_mcp.utils.context import BrazeContext
from braze_mcp.utils.http import build_http_client

from .test_utils import ValidationHelper


@pytest.fixture
def real_context() -> MagicMock:
    """Create a context with real API credentials for testing."""
    # Check if real API tests are enabled
    if not os.getenv("BRAZE_REAL_API_TEST"):
        pytest.skip("Real API tests disabled. Set BRAZE_REAL_API_TEST=1 to enable")

    api_key = os.getenv("BRAZE_API_KEY")
    base_url = os.getenv("BRAZE_BASE_URL")

    if not api_key:
        pytest.skip("BRAZE_API_KEY environment variable required for real API tests")
    if not base_url:
        pytest.skip("BRAZE_BASE_URL environment variable required for real API tests")

    # Create real HTTP client
    http_client = build_http_client(api_key)

    # Create mock context with real BrazeContext
    mock_ctx = MagicMock()
    mock_ctx.request_context = MagicMock()
    mock_ctx.request_context.lifespan_context = BrazeContext(
        api_key=api_key,
        base_url=base_url,
        http_client=http_client,
    )
    return mock_ctx


@pytest.fixture
def invalid_auth_context() -> MagicMock:
    """Create a context with invalid API credentials for testing auth failures."""
    # Check if real API tests are enabled
    if not os.getenv("BRAZE_REAL_API_TEST"):
        pytest.skip("Real API tests disabled. Set BRAZE_REAL_API_TEST=1 to enable")

    invalid_api_key = "invalid_key_12345"
    http_client = build_http_client(invalid_api_key)
    mock_ctx = MagicMock()
    mock_ctx.request_context = MagicMock()
    mock_ctx.request_context.lifespan_context = BrazeContext(
        api_key=invalid_api_key,
        base_url=os.getenv("BRAZE_BASE_URL", "https://rest.iad-01.braze.com"),
        http_client=http_client,
    )
    return mock_ctx


@pytest.fixture
def validation_helper():
    """Provide validation helper for tests."""
    return ValidationHelper()
