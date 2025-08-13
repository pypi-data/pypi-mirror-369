from unittest.mock import patch

import pytest

from braze_mcp.models import ContentBlockInfo, ContentBlocksResponse
from braze_mcp.tools.templates import (
    get_content_block_info,
    get_content_blocks,
)


@pytest.fixture
def sample_content_blocks_data():
    """Sample data for content blocks endpoint."""
    return {
        "count": 2,
        "content_blocks": [
            {
                "content_block_id": "cb_12345",
                "name": "Welcome Email Header",
                "content_type": "html",
                "liquid_tag": "{% contentblock 'cb_12345' %}",
                "inclusion_count": 15,
                "created_at": "2023-01-15T10:30:00.000Z",
                "last_edited": "2023-06-20T14:45:00.000Z",
                "tags": ["email", "welcome", "header"],
            },
            {
                "content_block_id": "cb_67890",
                "name": "Footer Disclaimer",
                "content_type": "text",
                "liquid_tag": "{% contentblock 'cb_67890' %}",
                "inclusion_count": 42,
                "created_at": "2023-02-01T08:15:00.000Z",
                "last_edited": "2023-05-10T12:30:00.000Z",
                "tags": ["footer", "legal"],
            },
        ],
    }


@pytest.fixture
def empty_content_blocks_data():
    """Sample data for empty content blocks response."""
    return {"count": 0, "content_blocks": []}


@pytest.fixture
def sample_content_block_info_data():
    """Sample data for content block info endpoint without inclusion data."""
    return {
        "content_block_id": "92ed12a2-efd5-4967-9283-cfb8a5254581",
        "name": "1TestErikaSemtei1",
        "content": '<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%">\n\t<tbody>\n\t\t<tr>\n\t\t\t<td align="center">\n\t\t\t<div><img data-bind="attr: {\'title\': $data.name, \'src\': $data.fullUrl}" src="https://cdn.braze.eu/appboy/communication/assets/image_assets/images/5c140b8c3f0da278c03465db/original.png?1544817548" style="width: 100%;" title="hearts_centered.png" /><br />\n\t\t\t </div>\n\n\t\t\t<div style="text-align: center;"><strong><span style="font-size:18px;"><span style="font-family:Arial,Helvetica Neue,Helvetica,sans-serif;">Test Test Test</span></span></strong><br />\n\t\t\t </div>\n\t\t\t</td>\n\t\t</tr>\n\t\t<tr>\n\t\t\t<td align="center"><span style="color:696969;"><span style="font-family:Arial,Helvetica Neue,Helvetica,sans-serif;"><span style="font-size:14px;">I\'m Erika. This is a Test <br />\n\t\t\t<br />\n\t\t</span></span></span></td>\n\t\t</tr>\n\t</tbody>\n</table>\n',
        "description": "",
        "content_type": "html",
        "created_at": "2019-01-17T10:55:57.174+00:00",
        "last_edited": "2019-01-17T10:57:41.528+00:00",
        "tags": [],
        "inclusion_count": 16,
        "message": "success",
    }


@pytest.fixture
def sample_content_block_info_with_inclusion_data():
    """Sample data for content block info endpoint with inclusion data."""
    return {
        "content_block_id": "92ed12a2-efd5-4967-9283-cfb8a5254581",
        "name": "1TestErikaSemtei1",
        "content": '<table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%">\n\t<tbody>\n\t\t<tr>\n\t\t\t<td align="center">\n\t\t\t<div><img data-bind="attr: {\'title\': $data.name, \'src\': $data.fullUrl}" src="https://cdn.braze.eu/appboy/communication/assets/image_assets/images/5c140b8c3f0da278c03465db/original.png?1544817548" style="width: 100%;" title="hearts_centered.png" /><br />\n\t\t\t </div>\n\n\t\t\t<div style="text-align: center;"><strong><span style="font-size:18px;"><span style="font-family:Arial,Helvetica Neue,Helvetica,sans-serif;">Test Test Test</span></span></strong><br />\n\t\t\t </div>\n\t\t\t</td>\n\t\t</tr>\n\t\t<tr>\n\t\t\t<td align="center"><span style="color:696969;"><span style="font-family:Arial,Helvetica Neue,Helvetica,sans-serif;"><span style="font-size:14px;">I\'m Erika. This is a Test <br />\n\t\t\t<br />\n\t\t</span></span></span></td>\n\t\t</tr>\n\t</tbody>\n</table>\n',
        "description": "",
        "content_type": "html",
        "created_at": "2019-01-17T10:55:57.174+00:00",
        "last_edited": "2019-01-17T10:57:41.528+00:00",
        "tags": [],
        "inclusion_count": 16,
        "message": "success",
        "inclusion_data": [
            {
                "campaign_id": "4bd97844-09e4-4b84-9de3-943cd3fdc420",
                "message_variation_id": "4090cce3-ebd4-40dd-833d-046872660ffa",
            },
            {
                "canvas_step_id": "a6764072-f389-4c67-86fc-6607be1be7dd",
                "message_variation_id": "4222dd15-1cbc-4c9d-be99-d02e8a7850ed",
            },
            {
                "canvas_step_id": "f757bd0f-0deb-4aab-81a5-883b175209d0",
                "message_variation_id": "3631904f-9c2a-4777-940b-118820ab7116",
            },
        ],
    }


@pytest.fixture
def sample_email_templates_data():
    """Sample data for email templates endpoint."""
    return {
        "count": 2,
        "templates": [
            {
                "email_template_id": "template_12345",
                "template_name": "Welcome Email Template",
                "created_at": "2023-01-15T10:30:00.000Z",
                "updated_at": "2023-06-20T14:45:00.000Z",
                "tags": ["welcome", "onboarding", "email"],
            },
            {
                "email_template_id": "template_67890",
                "template_name": "Newsletter Template",
                "created_at": "2023-02-01T08:15:00.000Z",
                "updated_at": "2023-05-10T12:30:00.000Z",
                "tags": ["newsletter", "marketing"],
            },
        ],
    }


@pytest.fixture
def empty_email_templates_data():
    """Sample data for empty email templates response."""
    return {"count": 0, "templates": []}


class TestGetContentBlocks:
    """Test get_content_blocks function"""

    @pytest.mark.asyncio
    async def test_success_response_with_content_blocks(
        self, mock_context, mock_braze_context, sample_content_blocks_data
    ):
        """Test successful content blocks retrieval with data."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=SuccessResponse(data=sample_content_blocks_data, headers={}),
            ) as mock_request,
        ):
            result = await get_content_blocks(mock_context)

            assert isinstance(result, ContentBlocksResponse)
            assert result.count == 2
            assert len(result.content_blocks) == 2

            # Check first content block
            first_block = result.content_blocks[0]
            assert first_block.content_block_id == "cb_12345"
            assert first_block.name == "Welcome Email Header"
            assert first_block.content_type == "html"
            assert first_block.liquid_tag == "{% contentblock 'cb_12345' %}"
            assert first_block.inclusion_count == 15
            assert first_block.created_at == "2023-01-15T10:30:00.000Z"
            assert first_block.last_edited == "2023-06-20T14:45:00.000Z"
            assert first_block.tags == ["email", "welcome", "header"]

            # Check second content block
            second_block = result.content_blocks[1]
            assert second_block.content_block_id == "cb_67890"
            assert second_block.name == "Footer Disclaimer"
            assert second_block.content_type == "text"
            assert second_block.inclusion_count == 42
            assert second_block.tags == ["footer", "legal"]

            # Verify call was made correctly
            call_args = mock_request.call_args
            assert call_args[0][0] == mock_braze_context.http_client
            assert call_args[0][1] == mock_braze_context.base_url
            assert call_args[0][2] == "content_blocks/list"
            params = call_args[0][3]
            assert len(params) == 4

    @pytest.mark.asyncio
    async def test_success_response_with_parameters(
        self, mock_context, mock_braze_context, sample_content_blocks_data
    ):
        """Test content blocks retrieval with all parameters."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=SuccessResponse(data=sample_content_blocks_data, headers={}),
            ) as mock_request,
        ):
            result = await get_content_blocks(
                mock_context,
                modified_after="2023-01-01T00:00:00.000Z",
                modified_before="2023-12-31T23:59:59.999Z",
                limit=50,
                offset=10,
            )

            assert isinstance(result, ContentBlocksResponse)
            assert result.count == 2

            # Verify parameters were passed correctly
            call_args = mock_request.call_args
            params = call_args[0][3]
            assert params["modified_after"] == "2023-01-01T00:00:00.000Z"
            assert params["modified_before"] == "2023-12-31T23:59:59.999Z"
            assert params["limit"] == 50
            assert params["offset"] == 10

    @pytest.mark.asyncio
    async def test_success_response_empty_content_blocks(
        self, mock_context, mock_braze_context, empty_content_blocks_data
    ):
        """Test successful response with no content blocks."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=SuccessResponse(data=empty_content_blocks_data, headers={}),
            ),
        ):
            result = await get_content_blocks(mock_context)

            assert isinstance(result, ContentBlocksResponse)
            assert result.count == 0
            assert len(result.content_blocks) == 0

    @pytest.mark.asyncio
    async def test_api_error_response(self, mock_context, mock_braze_context):
        """Test handling of API error response."""
        from braze_mcp.utils.http import FailureResponse

        error_data = {"error": "Invalid API key"}

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=FailureResponse(data=error_data, error=Exception("API Error")),
            ),
        ):
            result = await get_content_blocks(mock_context)

            # Should return error dict when there's an API error
            assert isinstance(result, dict)
            assert result == error_data

    @pytest.mark.asyncio
    async def test_invalid_response_format(self, mock_context, mock_braze_context):
        """Test handling of invalid response format that can't be parsed by pydantic."""
        from braze_mcp.utils.http import SuccessResponse

        invalid_data = {"invalid_field": "this doesn't match the expected schema"}

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ),
        ):
            result = await get_content_blocks(mock_context)

            # Should return raw dict when pydantic parsing fails
            assert isinstance(result, dict)
            assert result == invalid_data

    @pytest.mark.asyncio
    async def test_content_blocks_unexpected_response_type(self, mock_context, mock_braze_context):
        """Test content blocks handles unexpected response type"""
        from unittest.mock import MagicMock

        # Create a mock object that isn't SuccessResponse or FailureResponse
        unexpected_response = MagicMock()
        unexpected_response.__class__.__name__ = "UnexpectedResponse"

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=unexpected_response,
            ),
            patch("braze_mcp.tools.templates.logger.error") as mock_logger,
        ):
            result = await get_content_blocks(mock_context)

            assert isinstance(result, dict)
            assert "error" in result
            # Check that we get a standardized error response
            assert result["success"] is False
            assert result["error"]["error_type"] == "unexpected_error"
            mock_logger.assert_called_once_with(
                f"Unexpected response type: {type(unexpected_response)}"
            )


class TestGetContentBlockInfo:
    """Test get_content_block_info function"""

    @pytest.mark.asyncio
    async def test_success_response_without_inclusion_data(
        self, mock_context, mock_braze_context, sample_content_block_info_data
    ):
        """Test successful content block info retrieval without inclusion data."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=SuccessResponse(data=sample_content_block_info_data, headers={}),
            ) as mock_request,
        ):
            result = await get_content_block_info(
                mock_context, content_block_id="92ed12a2-efd5-4967-9283-cfb8a5254581"
            )

            assert isinstance(result, ContentBlockInfo)
            assert result.content_block_id == "92ed12a2-efd5-4967-9283-cfb8a5254581"
            assert result.name == "1TestErikaSemtei1"
            assert result.content_type == "html"
            assert result.description == ""
            assert result.tags == []
            assert result.inclusion_count == 16
            assert result.message == "success"
            assert result.inclusion_data is None
            assert result.created_at == "2019-01-17T10:55:57.174+00:00"
            assert result.last_edited == "2019-01-17T10:57:41.528+00:00"
            assert "Test Test Test" in result.content

            call_args = mock_request.call_args
            assert call_args[0][0] == mock_braze_context.http_client
            assert call_args[0][1] == mock_braze_context.base_url
            assert call_args[0][2] == "content_blocks/info"
            params = call_args[0][3]
            assert params["content_block_id"] == "92ed12a2-efd5-4967-9283-cfb8a5254581"
            assert params["include_inclusion_data"] is False

    @pytest.mark.asyncio
    async def test_success_response_with_inclusion_data(
        self, mock_context, mock_braze_context, sample_content_block_info_with_inclusion_data
    ):
        """Test successful content block info retrieval with inclusion data."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=SuccessResponse(
                    data=sample_content_block_info_with_inclusion_data, headers={}
                ),
            ) as mock_request,
        ):
            result = await get_content_block_info(
                mock_context,
                content_block_id="92ed12a2-efd5-4967-9283-cfb8a5254581",
                include_inclusion_data=True,
            )

            assert isinstance(result, ContentBlockInfo)
            assert result.content_block_id == "92ed12a2-efd5-4967-9283-cfb8a5254581"
            assert result.name == "1TestErikaSemtei1"
            assert result.inclusion_count == 16
            assert result.message == "success"

            # Check inclusion data
            assert result.inclusion_data is not None
            assert len(result.inclusion_data) == 3

            # Check first inclusion (campaign)
            first_inclusion = result.inclusion_data[0]
            assert first_inclusion.campaign_id == "4bd97844-09e4-4b84-9de3-943cd3fdc420"
            assert first_inclusion.message_variation_id == "4090cce3-ebd4-40dd-833d-046872660ffa"
            assert first_inclusion.canvas_step_id is None

            # Check second inclusion (canvas step)
            second_inclusion = result.inclusion_data[1]
            assert second_inclusion.canvas_step_id == "a6764072-f389-4c67-86fc-6607be1be7dd"
            assert second_inclusion.message_variation_id == "4222dd15-1cbc-4c9d-be99-d02e8a7850ed"
            assert second_inclusion.campaign_id is None

            call_args = mock_request.call_args
            params = call_args[0][3]
            assert params["content_block_id"] == "92ed12a2-efd5-4967-9283-cfb8a5254581"
            assert params["include_inclusion_data"] is True

    @pytest.mark.asyncio
    async def test_api_error_response(self, mock_context, mock_braze_context):
        """Test handling of API error response."""
        from braze_mcp.utils.http import FailureResponse

        error_data = {"error": "Content Block not found"}

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=FailureResponse(data=error_data, error=Exception("API Error")),
            ),
        ):
            result = await get_content_block_info(mock_context, content_block_id="invalid-id")

            # Should return error dict when there's an API error
            assert isinstance(result, dict)
            assert result == error_data

    @pytest.mark.asyncio
    async def test_invalid_response_format(self, mock_context, mock_braze_context):
        """Test handling of invalid response format that can't be parsed by pydantic."""
        from braze_mcp.utils.http import SuccessResponse

        invalid_data = {"invalid_field": "this doesn't match the expected schema"}

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ),
        ):
            result = await get_content_block_info(mock_context, content_block_id="some-id")

            # Should return raw dict when pydantic parsing fails
            assert isinstance(result, dict)
            assert result == invalid_data

    @pytest.mark.asyncio
    async def test_unexpected_response_type(self, mock_context, mock_braze_context):
        """Test content block info handles unexpected response type"""
        from unittest.mock import MagicMock

        # Create a mock object that isn't SuccessResponse or FailureResponse
        unexpected_response = MagicMock()
        unexpected_response.__class__.__name__ = "UnexpectedResponse"

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=unexpected_response,
            ),
            patch("braze_mcp.tools.templates.logger.error") as mock_logger,
        ):
            result = await get_content_block_info(mock_context, content_block_id="some-id")

            assert isinstance(result, dict)
            assert "error" in result
            # Check that we get a standardized error response
            assert result["success"] is False
            assert result["error"]["error_type"] == "unexpected_error"
            mock_logger.assert_called_once_with(
                f"Unexpected response type: {type(unexpected_response)}"
            )
