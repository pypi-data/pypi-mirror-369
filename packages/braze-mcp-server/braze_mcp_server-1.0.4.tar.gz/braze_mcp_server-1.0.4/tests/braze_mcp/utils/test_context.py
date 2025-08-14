import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from braze_mcp.utils.context import (
    BrazeContext,
    _get_required_env,
    _normalize_base_url,
    braze_lifespan,
    get_braze_context,
)


class TestGetRequiredEnv:
    """Test the _get_required_env function"""

    def test_get_required_env_success(self):
        """Test getting a required environment variable successfully"""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = _get_required_env("TEST_VAR")
            assert result == "test_value"

    def test_get_required_env_missing_required(self):
        """Test that missing required env var raises ValueError"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="TEST_VAR environment variable must be set"):
                _get_required_env("TEST_VAR")

    def test_get_required_env_empty_string_treated_as_none(self):
        """Test that empty string is treated as None"""
        with patch.dict(os.environ, {"EMPTY_VAR": ""}):
            with pytest.raises(ValueError, match="EMPTY_VAR environment variable must be set"):
                _get_required_env("EMPTY_VAR")


class TestBrazeLifespan:
    """Test the braze_lifespan context manager"""

    @pytest.mark.asyncio
    async def test_braze_lifespan_success(self):
        """Test successful braze lifespan initialization and cleanup"""
        mock_server = MagicMock()
        mock_client = AsyncMock()

        with patch.dict(
            os.environ,
            {"BRAZE_API_KEY": "test_key", "BRAZE_BASE_URL": "https://test.com"},
        ):
            with patch("braze_mcp.utils.context.load_dotenv") as mock_load_dotenv:
                with patch(
                    "braze_mcp.utils.context.build_http_client",
                    return_value=mock_client,
                ) as mock_build_client:
                    async with braze_lifespan(mock_server) as context:
                        assert isinstance(context, BrazeContext)
                        assert context.api_key == "test_key"
                        assert context.base_url == "https://test.com"
                        assert context.http_client == mock_client

                    mock_load_dotenv.assert_called_once()
                    mock_build_client.assert_called_once_with("test_key")
                    mock_client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_braze_lifespan_missing_api_key(self):
        """Test braze lifespan with missing API key"""
        mock_server = MagicMock()

        with patch.dict(os.environ, {"BRAZE_BASE_URL": "https://test.com"}, clear=True):
            with patch("braze_mcp.utils.context.load_dotenv"):
                with pytest.raises(
                    ValueError, match="BRAZE_API_KEY environment variable must be set"
                ):
                    async with braze_lifespan(mock_server):
                        pass

    @pytest.mark.asyncio
    async def test_braze_lifespan_missing_base_url(self):
        """Test braze lifespan with missing base URL"""
        mock_server = MagicMock()

        with patch.dict(os.environ, {"BRAZE_API_KEY": "test_key"}, clear=True):
            with patch("braze_mcp.utils.context.load_dotenv"):
                with pytest.raises(
                    ValueError, match="BRAZE_BASE_URL environment variable must be set"
                ):
                    async with braze_lifespan(mock_server):
                        pass

    @pytest.mark.asyncio
    async def test_braze_lifespan_cleanup_on_exception(self):
        """Test that HTTP client is cleaned up even when exception occurs"""
        mock_server = MagicMock()
        mock_client = AsyncMock()

        with patch.dict(
            os.environ,
            {"BRAZE_API_KEY": "test_key", "BRAZE_BASE_URL": "https://test.com"},
        ):
            with patch("braze_mcp.utils.context.load_dotenv"):
                with patch(
                    "braze_mcp.utils.context.build_http_client",
                    return_value=mock_client,
                ):
                    with pytest.raises(RuntimeError):
                        async with braze_lifespan(mock_server):
                            raise RuntimeError("Test exception")

                    mock_client.aclose.assert_called_once()


class TestNormalizeBaseUrl:
    """Test the _normalize_base_url function"""

    def test_normalize_base_url_with_https(self):
        """Test URL that already has https:// protocol"""
        url = "https://anna.braze.com"
        result = _normalize_base_url(url)
        assert result == "https://anna.braze.com"

    def test_normalize_base_url_with_http(self):
        """Test URL that already has http:// protocol"""
        url = "http://anna.braze.com"
        result = _normalize_base_url(url)
        assert result == "http://anna.braze.com"

    def test_normalize_base_url_without_protocol(self):
        """Test URL without protocol - should add https://"""
        url = "anna.braze.com"
        result = _normalize_base_url(url)
        assert result == "https://anna.braze.com"

    def test_normalize_base_url_empty(self):
        """Test empty URL"""
        url = ""
        result = _normalize_base_url(url)
        assert result == ""

    def test_normalize_base_url_with_subdomain(self):
        """Test URL with subdomain without protocol"""
        url = "rest.iad-01.braze.com"
        result = _normalize_base_url(url)
        assert result == "https://rest.iad-01.braze.com"


class TestGetBrazeContext:
    """Test the get_braze_context function"""

    def test_get_braze_context_success(self):
        """Test successful context retrieval"""
        mock_braze_context = BrazeContext(
            api_key="test_key", base_url="https://test.com", http_client=MagicMock()
        )

        mock_ctx = MagicMock()
        mock_ctx.request_context.lifespan_context = mock_braze_context

        with patch("braze_mcp.utils.context.logger.info") as mock_info:
            result = get_braze_context(mock_ctx)
            assert result == mock_braze_context
            mock_info.assert_any_call("Attempting to get Braze context")
            mock_info.assert_any_call("Successfully retrieved Braze context")

    def test_get_braze_context_none_context(self):
        """Test context retrieval with None context"""
        with patch("braze_mcp.utils.context.logger.error") as mock_error:
            with pytest.raises(ValueError, match="Context is None"):
                get_braze_context(None)
            mock_error.assert_called_with("Context is None")

    def test_get_braze_context_no_request_context(self):
        """Test context retrieval without request_context attribute"""
        mock_ctx = MagicMock()
        del mock_ctx.request_context

        with patch("braze_mcp.utils.context.logger.error") as mock_error:
            with pytest.raises(ValueError, match="request_context not found in Context"):
                get_braze_context(mock_ctx)
            mock_error.assert_called_with("request_context not found in Context")

    def test_get_braze_context_no_lifespan_context(self):
        """Test context retrieval without lifespan_context attribute"""
        mock_ctx = MagicMock()
        del mock_ctx.request_context.lifespan_context

        with patch("braze_mcp.utils.context.logger.error") as mock_error:
            with pytest.raises(ValueError, match="lifespan_context not found in request_context"):
                get_braze_context(mock_ctx)
            mock_error.assert_called_with("lifespan_context not found in request_context")
