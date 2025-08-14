from unittest.mock import MagicMock, patch

import pytest

from braze_mcp.tools.custom_attributes import get_custom_attributes


@pytest.fixture
def sample_custom_attributes_data():
    return {
        "message": "success",
        "attributes": [
            {
                "array_length": None,
                "data_type": "String",
                "description": "User's first name",
                "name": "first_name",
                "status": "Active",
                "tag_names": ["user_data", "profile"],
            },
            {
                "array_length": 10,
                "data_type": "Array",
                "description": "User's preferences",
                "name": "preferences",
                "status": "Active",
                "tag_names": ["user_data"],
            },
            {
                "array_length": None,
                "data_type": "Boolean",
                "description": None,
                "name": "is_premium",
                "status": "Blocklisted",
                "tag_names": [],
            },
        ],
    }


@pytest.fixture
def sample_response_headers():
    return {
        "content-type": "application/json",
        "link": '<https://test.braze.com/custom_attributes/?cursor=abc123>; rel="next"',
    }


class TestGetCustomAttributes:
    """Test get_custom_attributes function"""

    @pytest.mark.asyncio
    async def test_get_custom_attributes_success(
        self,
        mock_context,
        mock_braze_context,
        sample_custom_attributes_data,
        sample_response_headers,
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.custom_attributes.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.custom_attributes.make_request",
                return_value=SuccessResponse(
                    data=sample_custom_attributes_data,
                    headers=sample_response_headers,
                ),
            ) as mock_request:
                with patch(
                    "braze_mcp.tools.custom_attributes.extract_cursor_from_link_header",
                    return_value="abc123",
                ):
                    result = await get_custom_attributes(mock_context)

                    from braze_mcp.models import CustomAttributesWithPagination

                    assert isinstance(result, CustomAttributesWithPagination)
                    assert result.message == "success"
                    assert len(result.attributes) == 3
                    assert result.attributes[0].name == "first_name"
                    assert result.attributes[1].name == "preferences"
                    assert result.attributes[2].name == "is_premium"

                    # Check pagination info
                    pagination = result.pagination_info
                    assert pagination.current_page_count == 3
                    assert pagination.has_more_pages
                    assert pagination.next_cursor == "abc123"
                    assert pagination.max_per_page == 50
                    assert pagination.link_header == sample_response_headers["link"]

                    # Verify call was made correctly - new signature: client, base_url, url_path, params
                    call_args = mock_request.call_args
                    assert call_args[0][0] == mock_braze_context.http_client  # client
                    assert call_args[0][1] == mock_braze_context.base_url  # base_url
                    assert call_args[0][2] == "custom_attributes"  # url_path
                    params = call_args[0][3]  # params
                    assert params == {}

    @pytest.mark.asyncio
    async def test_get_custom_attributes_with_cursor(
        self,
        mock_context,
        mock_braze_context,
        sample_custom_attributes_data,
        sample_response_headers,
    ):
        cursor = "test_cursor_123"
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.custom_attributes.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.custom_attributes.make_request",
                return_value=SuccessResponse(
                    data=sample_custom_attributes_data,
                    headers=sample_response_headers,
                ),
            ) as mock_request:
                with patch(
                    "braze_mcp.tools.custom_attributes.extract_cursor_from_link_header",
                    return_value="abc123",
                ):
                    await get_custom_attributes(mock_context, cursor=cursor)

                    # Verify cursor parameter was passed correctly
                    call_args = mock_request.call_args
                    assert call_args[0][0] == mock_braze_context.http_client  # client
                    assert call_args[0][1] == mock_braze_context.base_url  # base_url
                    assert call_args[0][2] == "custom_attributes"  # url_path
                    params = call_args[0][3]  # params
                    assert params["cursor"] == cursor

    @pytest.mark.asyncio
    async def test_get_custom_attributes_no_link_header(
        self, mock_context, mock_braze_context, sample_custom_attributes_data
    ):
        response_headers = {"content-type": "application/json"}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.custom_attributes.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.custom_attributes.make_request",
                return_value=SuccessResponse(
                    data=sample_custom_attributes_data, headers=response_headers
                ),
            ):
                with patch(
                    "braze_mcp.tools.custom_attributes.extract_cursor_from_link_header",
                    return_value=None,
                ):
                    result = await get_custom_attributes(mock_context)

                    # Check pagination info when no next page
                    pagination = result.pagination_info
                    assert not pagination.has_more_pages
                    assert pagination.next_cursor is None
                    assert pagination.link_header is None

    @pytest.mark.asyncio
    async def test_get_custom_attributes_request_failure(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.custom_attributes.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.custom_attributes.make_request",
                return_value=FailureResponse(
                    data={"error": "Request failed"},
                    error=Exception("Request failed"),
                ),
            ):
                result = await get_custom_attributes(mock_context)

                assert isinstance(result, dict)
                assert "error" in result
                assert result["error"] == "Request failed"

    @pytest.mark.asyncio
    async def test_get_custom_attributes_parsing_error(self, mock_context, mock_braze_context):
        """Test get custom attributes returns the raw response when schema validation fails"""
        invalid_data = {"message": "success", "attributes": [{"invalid": "data"}]}
        response_headers = {"content-type": "application/json"}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.custom_attributes.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.custom_attributes.make_request",
                return_value=SuccessResponse(data=invalid_data, headers=response_headers),
            ):
                with patch("braze_mcp.tools.custom_attributes.logger.exception") as mock_logger:
                    result = await get_custom_attributes(mock_context)

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_custom_attributes_empty_attributes(self, mock_context, mock_braze_context):
        empty_data = {"message": "success", "attributes": []}
        response_headers = {"content-type": "application/json"}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.custom_attributes.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.custom_attributes.make_request",
                return_value=SuccessResponse(data=empty_data, headers=response_headers),
            ):
                with patch(
                    "braze_mcp.tools.custom_attributes.extract_cursor_from_link_header",
                    return_value=None,
                ):
                    result = await get_custom_attributes(mock_context)

                    from braze_mcp.models import CustomAttributesWithPagination

                    assert isinstance(result, CustomAttributesWithPagination)
                    assert result.message == "success"
                    assert len(result.attributes) == 0

                    # Check pagination info
                    pagination = result.pagination_info
                    assert pagination.current_page_count == 0
                    assert not pagination.has_more_pages
                    assert pagination.next_cursor is None

    @pytest.mark.asyncio
    async def test_get_custom_attributes_unexpected_response_type(
        self, mock_context, mock_braze_context
    ):
        """Test custom attributes handles unexpected response type"""

        # Create a mock object that isn't SuccessResponse or FailureResponse
        unexpected_response = MagicMock()
        unexpected_response.__class__.__name__ = "UnexpectedResponse"

        with patch(
            "braze_mcp.tools.custom_attributes.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.custom_attributes.make_request",
                return_value=unexpected_response,
            ):
                with patch("braze_mcp.tools.custom_attributes.logger.error") as mock_logger:
                    result = await get_custom_attributes(mock_context)

                    assert isinstance(result, dict)
                    assert "error" in result
                    # Check that we get a standardized error response
                    assert result["success"] is False
                    assert result["error"]["error_type"] == "unexpected_error"
                    mock_logger.assert_called_once_with(
                        f"Unexpected response type: {type(unexpected_response)}"
                    )
