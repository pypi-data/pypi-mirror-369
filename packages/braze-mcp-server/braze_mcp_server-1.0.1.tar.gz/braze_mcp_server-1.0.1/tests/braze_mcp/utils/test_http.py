import json
from logging import Logger
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from pydantic import BaseModel

from braze_mcp.utils.http import (
    FailureResponse,
    SuccessResponse,
    _sanitize,
    build_headers,
    build_http_client,
    extract_cursor_from_link_header,
    handle_response,
    make_request,
)


class TestBuildHeaders:
    """Test the build_headers function"""

    def test_build_headers_basic(self):
        """Test basic header building"""
        api_key = "test_api_key"
        headers = build_headers(api_key)

        expected_headers = {
            "Accept": "application/json",
            "Authorization": "Bearer test_api_key",
            "X-Braze-MCP-Source": "local-v1.0.0",
        }

        assert headers == expected_headers

    def test_build_headers_empty_key(self):
        """Test header building with empty API key"""
        api_key = ""
        with pytest.raises(ValueError, match="api_key must be a non-empty value"):
            build_headers(api_key)

    def test_build_headers_none_key(self):
        """Test header building with None API key"""
        api_key = None
        with pytest.raises(ValueError, match="api_key must be a non-empty value"):
            build_headers(api_key)


class TestBuildHttpClient:
    """Test the build_http_client function"""

    def test_build_http_client_default_timeout(self):
        """Test HTTP client building with default timeout"""
        api_key = "test_api_key"

        with patch("braze_mcp.utils.http.httpx.AsyncClient") as mock_client:
            build_http_client(api_key)

            expected_headers = {
                "Accept": "application/json",
                "Authorization": "Bearer test_api_key",
                "X-Braze-MCP-Source": "local-v1.0.0",
            }

            mock_client.assert_called_once_with(headers=expected_headers, timeout=10.0)

    def test_build_http_client_custom_timeout(self):
        """Test HTTP client building with custom timeout"""
        api_key = "test_api_key"
        timeout = 60.0

        with patch("braze_mcp.utils.http.httpx.AsyncClient") as mock_client:
            build_http_client(api_key, timeout)

            expected_headers = {
                "Accept": "application/json",
                "Authorization": "Bearer test_api_key",
                "X-Braze-MCP-Source": "local-v1.0.0",
            }

            mock_client.assert_called_once_with(headers=expected_headers, timeout=60.0)


class TestExtractCursorFromLinkHeader:
    """Test the extract_cursor_from_link_header function"""

    def test_extract_cursor_success(self):
        """Test successful cursor extraction"""
        link_header = '<https://anna.braze.com/custom_attributes/?cursor=c2tpcDo1MA==>; rel="next"'
        cursor = extract_cursor_from_link_header(link_header)
        assert cursor == "c2tpcDo1MA=="

    def test_extract_cursor_with_additional_params(self):
        """Test cursor extraction with additional URL parameters"""
        link_header = '<https://anna.braze.com/custom_attributes/?page=2&cursor=c2tpcDoxMDA=&limit=50>; rel="next"'
        cursor = extract_cursor_from_link_header(link_header)
        assert cursor == "c2tpcDoxMDA="

    def test_extract_cursor_no_next_link(self):
        """Test cursor extraction when no next link exists"""
        link_header = '<https://anna.braze.com/custom_attributes/?cursor=c2tpcDow>; rel="prev"'
        cursor = extract_cursor_from_link_header(link_header)
        assert cursor is None

    def test_extract_cursor_no_cursor_param(self):
        """Test cursor extraction when URL has no cursor parameter"""
        link_header = '<https://anna.braze.com/custom_attributes/?page=2>; rel="next"'
        cursor = extract_cursor_from_link_header(link_header)
        assert cursor is None

    def test_extract_cursor_empty_header(self):
        """Test cursor extraction with empty header"""
        cursor = extract_cursor_from_link_header("")
        assert cursor is None

    def test_extract_cursor_none_header(self):
        """Test cursor extraction with None header"""
        cursor = extract_cursor_from_link_header(None)
        assert cursor is None

    def test_extract_cursor_malformed_header(self):
        """Test cursor extraction with malformed header"""
        link_header = "invalid header format"
        cursor = extract_cursor_from_link_header(link_header)
        assert cursor is None


class TestSanitize:
    """Test the _sanitize function"""

    def test_sanitize_removes_none_values(self):
        """Test that sanitize removes None values"""
        data = {"key1": "value1", "key2": None, "key3": "value3"}
        result = _sanitize(data)
        assert result == {"key1": "value1", "key3": "value3"}

    def test_sanitize_empty_dict(self):
        """Test sanitize with empty dict"""
        data = {}
        result = _sanitize(data)
        assert result is None

    def test_sanitize_all_none_values(self):
        """Test sanitize with all None values"""
        data = {"key1": None, "key2": None}
        result = _sanitize(data)
        assert result == {}

    def test_sanitize_no_none_values(self):
        """Test sanitize with no None values"""
        data = {"key1": "value1", "key2": "value2"}
        result = _sanitize(data)
        assert result == {"key1": "value1", "key2": "value2"}

    def test_sanitize_none_input(self):
        """Test sanitize with None input"""
        result = _sanitize(None)
        assert result is None

    def test_sanitize_preserves_other_falsy_values(self):
        """Test that sanitize preserves other falsy values like 0, False, empty string"""
        data = {"key1": 0, "key2": False, "key3": "", "key4": None, "key5": "value"}
        result = _sanitize(data)
        assert result == {"key1": 0, "key2": False, "key3": "", "key5": "value"}


class TestMakeRequest:
    """Test the make_request function"""

    @pytest.mark.asyncio
    async def test_make_request_success(self):
        """Test successful HTTP request"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response

        result = await make_request(
            client=mock_client,
            base_url="https://api.braze.com",
            url_path="/campaigns",
            params={"page": 1},
        )

        assert result is not None
        assert isinstance(result, SuccessResponse)
        assert result.data == {"success": True}

        mock_client.get.assert_called_once_with(
            "https://api.braze.com/campaigns",
            params={"page": 1},
            timeout=15.0,
        )

    @pytest.mark.asyncio
    async def test_make_request_with_none_params_and_headers(self):
        """Test request with None params and headers"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response

        result = await make_request(
            client=mock_client,
            base_url="https://api.braze.com",
            url_path="/campaigns",
            params=None,
        )

        assert result is not None
        assert isinstance(result, SuccessResponse)
        assert result.data == {"success": True}
        mock_client.get.assert_called_once_with(
            "https://api.braze.com/campaigns", params=None, timeout=15.0
        )

    @pytest.mark.asyncio
    async def test_make_request_sanitizes_params(self):
        """Test that request sanitizes parameters"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response

        await make_request(
            client=mock_client,
            base_url="https://api.braze.com",
            url_path="/campaigns",
            params={"page": 1, "unused": None},
        )

        mock_client.get.assert_called_once_with(
            "https://api.braze.com/campaigns",
            params={"page": 1},
            timeout=15.0,
        )

    @pytest.mark.asyncio
    async def test_make_request_json_decode_error(self):
        """Test request with JSON decode error"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response

        with patch("braze_mcp.utils.http.logger.exception") as mock_logger:
            result = await make_request(
                client=mock_client,
                base_url="https://api.braze.com",
                url_path="/campaigns",
            )

            assert isinstance(result, FailureResponse)
            assert "error" in result.data
            assert result.data["success"] is False
            assert result.data["error"]["error_type"] == "parsing_error"
            assert "Invalid JSON response from" in result.data["error"]["message"]
            mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_http_status_error(self):
        """Test request with HTTP status error"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=mock_response)
        mock_client.get.side_effect = http_error

        with patch("braze_mcp.utils.http.logger.exception") as mock_logger:
            result = await make_request(
                client=mock_client,
                base_url="https://api.braze.com",
                url_path="/campaigns",
            )

            assert isinstance(result, FailureResponse)
            assert "error" in result.data
            assert result.data["success"] is False
            assert result.data["error"]["error_type"] == "http_error"
            assert "Request failed with status code 404" in result.data["error"]["message"]
            mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_http_error(self):
        """Test request with general HTTP error"""
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")

        with patch("braze_mcp.utils.http.logger.exception") as mock_logger:
            result = await make_request(
                client=mock_client,
                base_url="https://api.braze.com",
                url_path="/campaigns",
            )

            assert isinstance(result, FailureResponse)
            assert "error" in result.data
            assert result.data["success"] is False
            assert result.data["error"]["error_type"] == "http_error"
            assert "Error occurred while making request" in result.data["error"]["message"]
            mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_unexpected_error(self):
        """Test request with unexpected error"""
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Unexpected error")

        with patch("braze_mcp.utils.http.logger.exception") as mock_logger:
            result = await make_request(
                client=mock_client,
                base_url="https://api.braze.com",
                url_path="/campaigns",
            )

            assert isinstance(result, FailureResponse)
            assert "error" in result.data
            assert result.data["success"] is False
            assert result.data["error"]["error_type"] == "internal_error"
            assert (
                "Unexpected error in make_request for /campaigns" in result.data["error"]["message"]
            )
            mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_url_joining(self):
        """Test that URL joining works correctly"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.headers = {}
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response

        await make_request(
            client=mock_client, base_url="https://api.braze.com/", url_path="/campaigns"
        )

        mock_client.get.assert_called_once_with(
            "https://api.braze.com/campaigns", params=None, timeout=15.0
        )


class SampleModel(BaseModel):
    """Sample Pydantic model for handle_response tests"""

    name: str
    value: int


class TestHandleResponse:
    """Test the handle_response function"""

    def test_handle_response_success_valid_data(self):
        """Test successful response with valid data that can be parsed by the model"""
        response_data = {"name": "test", "value": 42}
        response = SuccessResponse(
            data=response_data,
            headers={"X-Rate-Limit": "100", "Content-Type": "application/json"},
        )
        mock_logger = MagicMock(spec=Logger)

        result = handle_response(response, SampleModel, "test operation", mock_logger)

        assert isinstance(result, SampleModel)
        assert result.name == "test"
        assert result.value == 42
        mock_logger.exception.assert_not_called()
        mock_logger.error.assert_not_called()

    def test_handle_response_success_invalid_data(self):
        """Test successful response with invalid data that cannot be parsed by the model"""
        response_data = {"invalid": "data"}  # Missing required fields
        response = SuccessResponse(data=response_data, headers={})
        mock_logger = MagicMock(spec=Logger)

        result = handle_response(response, SampleModel, "test operation", mock_logger)

        assert result == response_data  # Should return raw data
        assert isinstance(result, dict)
        mock_logger.exception.assert_called_once()
        exception_call = mock_logger.exception.call_args[0][0]
        assert "Failed to parse test operation response with model" in exception_call

    def test_handle_response_failure(self):
        """Test failure response handling"""
        error_data = {"error": "API request failed", "status": 400}
        error = Exception("Request failed")
        response = FailureResponse(data=error_data, error=error)
        mock_logger = MagicMock(spec=Logger)

        result = handle_response(response, SampleModel, "test operation", mock_logger)

        assert result == error_data
        mock_logger.error.assert_called_once_with("Failed to test operation: Request failed")
        mock_logger.exception.assert_not_called()

    def test_handle_response_unexpected_response_type(self):
        """Test handling of unexpected response type"""
        unexpected_response = "not a valid response type"
        mock_logger = MagicMock(spec=Logger)

        result = handle_response(unexpected_response, SampleModel, "test operation", mock_logger)

        assert "error" in result
        assert result["success"] is False
        assert result["error"]["error_type"] == "unexpected_error"
        assert "Unexpected response type" in result["error"]["message"]
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Unexpected response type: <class 'str'>" in error_call
        mock_logger.exception.assert_not_called()

    def test_handle_response_success_with_extra_fields(self):
        """Test successful response with extra fields that should be ignored by model"""
        response_data = {
            "name": "test_with_extra",
            "value": 123,
            "extra_field": "should be ignored",
        }
        response = SuccessResponse(data=response_data, headers={})
        mock_logger = MagicMock(spec=Logger)

        result = handle_response(response, SampleModel, "test operation", mock_logger)

        assert isinstance(result, SampleModel)
        assert result.name == "test_with_extra"
        assert result.value == 123
        # Extra field should not be in the result (Pydantic ignores extra fields by default)
        assert not hasattr(result, "extra_field")
        mock_logger.exception.assert_not_called()
        mock_logger.error.assert_not_called()

    def test_handle_response_model_validation_type_error(self):
        """Test that specific validation errors are properly logged"""
        response_data = {"name": "test", "value": "not_an_integer"}  # Invalid type
        response = SuccessResponse(data=response_data, headers={})
        mock_logger = MagicMock(spec=Logger)

        result = handle_response(response, SampleModel, "validation test", mock_logger)

        assert result == response_data  # Should return raw data on validation failure
        mock_logger.exception.assert_called_once()
        exception_call = mock_logger.exception.call_args[0][0]
        assert "Failed to parse validation test response with model" in exception_call

    def test_handle_response_none_response(self):
        """Test handling of None response"""
        mock_logger = MagicMock(spec=Logger)

        result = handle_response(None, SampleModel, "none test", mock_logger)

        assert "error" in result
        assert result["success"] is False
        assert result["error"]["error_type"] == "unexpected_error"
        assert "Unexpected response type" in result["error"]["message"]
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Unexpected response type: <class 'NoneType'>" in error_call
