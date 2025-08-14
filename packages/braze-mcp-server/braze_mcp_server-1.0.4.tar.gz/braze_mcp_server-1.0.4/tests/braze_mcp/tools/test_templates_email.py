"""Tests for email templates tools."""

from unittest.mock import patch

import pytest

from braze_mcp.models import EmailTemplateInfo, EmailTemplatesResponse
from braze_mcp.tools.templates import get_email_template_info, get_email_templates


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


@pytest.fixture
def sample_email_template_info_data():
    """Sample data for email template info endpoint."""
    return {
        "email_template_id": "template_12345",
        "template_name": "Welcome Email Template",
        "description": "A welcome email template for new users",
        "subject": "Welcome to our platform!",
        "preheader": "Get started with your new account",
        "body": "<html><body><h1>Welcome!</h1><p>Thanks for joining us.</p></body></html>",
        "plaintext_body": "Welcome!\n\nThanks for joining us.",
        "should_inline_css": True,
        "tags": ["welcome", "onboarding", "email"],
        "created_at": "2023-01-15T10:30:00.000Z",
        "updated_at": "2023-06-20T14:45:00.000Z",
    }


@pytest.fixture
def sample_email_template_info_minimal_data():
    """Sample data for email template info endpoint with minimal fields."""
    return {
        "email_template_id": "template_minimal",
        "template_name": "Minimal Template",
        "description": "A minimal template",
        "subject": "Test Subject",
        "tags": ["test"],
        "created_at": "2023-01-15T10:30:00.000Z",
        "updated_at": "2023-06-20T14:45:00.000Z",
    }


class TestGetEmailTemplates:
    """Test get_email_templates function"""

    @pytest.mark.asyncio
    async def test_success_response_with_email_templates(
        self, mock_context, mock_braze_context, sample_email_templates_data
    ):
        """Test successful email templates retrieval with data."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=SuccessResponse(data=sample_email_templates_data, headers={}),
            ) as mock_request,
        ):
            result = await get_email_templates(mock_context)

            assert isinstance(result, EmailTemplatesResponse)
            assert result.count == 2
            assert len(result.templates) == 2

            # Check first template
            first_template = result.templates[0]
            assert first_template.email_template_id == "template_12345"
            assert first_template.template_name == "Welcome Email Template"
            assert first_template.created_at == "2023-01-15T10:30:00.000Z"
            assert first_template.updated_at == "2023-06-20T14:45:00.000Z"
            assert first_template.tags == ["welcome", "onboarding", "email"]

            # Check second template
            second_template = result.templates[1]
            assert second_template.email_template_id == "template_67890"
            assert second_template.template_name == "Newsletter Template"
            assert second_template.tags == ["newsletter", "marketing"]

            call_args = mock_request.call_args
            assert call_args[0][0] == mock_braze_context.http_client
            assert call_args[0][1] == mock_braze_context.base_url
            assert call_args[0][2] == "templates/email/list"
            params = call_args[0][3]
            assert len(params) == 4

    @pytest.mark.asyncio
    async def test_success_response_with_parameters(
        self, mock_context, mock_braze_context, sample_email_templates_data
    ):
        """Test email templates retrieval with all parameters."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=SuccessResponse(data=sample_email_templates_data, headers={}),
            ) as mock_request,
        ):
            result = await get_email_templates(
                mock_context,
                modified_after="2023-01-01T00:00:00.000Z",
                modified_before="2023-12-31T23:59:59.999Z",
                limit=50,
                offset=10,
            )

            assert isinstance(result, EmailTemplatesResponse)
            assert result.count == 2

            call_args = mock_request.call_args
            params = call_args[0][3]
            assert params["modified_after"] == "2023-01-01T00:00:00.000Z"
            assert params["modified_before"] == "2023-12-31T23:59:59.999Z"
            assert params["limit"] == 50
            assert params["offset"] == 10

    @pytest.mark.asyncio
    async def test_success_response_empty_email_templates(
        self, mock_context, mock_braze_context, empty_email_templates_data
    ):
        """Test successful response with no email templates."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=SuccessResponse(data=empty_email_templates_data, headers={}),
            ),
        ):
            result = await get_email_templates(mock_context)

            assert isinstance(result, EmailTemplatesResponse)
            assert result.count == 0
            assert len(result.templates) == 0

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
            result = await get_email_templates(mock_context)

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
            result = await get_email_templates(mock_context)

            # Should return raw dict when pydantic parsing fails
            assert isinstance(result, dict)
            assert result == invalid_data

    @pytest.mark.asyncio
    async def test_unexpected_response_type(self, mock_context, mock_braze_context):
        """Test email templates handles unexpected response type"""
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
            result = await get_email_templates(mock_context)

            assert isinstance(result, dict)
            assert "error" in result
            # Check that we get a standardized error response
            assert result["success"] is False
            assert result["error"]["error_type"] == "unexpected_error"
            mock_logger.assert_called_once_with(
                f"Unexpected response type: {type(unexpected_response)}"
            )


class TestGetEmailTemplateInfo:
    """Test get_email_template_info function"""

    @pytest.mark.asyncio
    async def test_success_response_with_full_data(
        self, mock_context, mock_braze_context, sample_email_template_info_data
    ):
        """Test successful email template info retrieval with full data."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=SuccessResponse(data=sample_email_template_info_data, headers={}),
            ) as mock_request,
        ):
            result = await get_email_template_info(mock_context, "template_12345")

            assert isinstance(result, EmailTemplateInfo)
            assert result.email_template_id == "template_12345"
            assert result.template_name == "Welcome Email Template"
            assert result.description == "A welcome email template for new users"
            assert result.subject == "Welcome to our platform!"
            assert result.preheader == "Get started with your new account"
            assert (
                result.body
                == "<html><body><h1>Welcome!</h1><p>Thanks for joining us.</p></body></html>"
            )
            assert result.plaintext_body == "Welcome!\n\nThanks for joining us."
            assert result.should_inline_css is True
            assert result.tags == ["welcome", "onboarding", "email"]
            assert result.created_at == "2023-01-15T10:30:00.000Z"
            assert result.updated_at == "2023-06-20T14:45:00.000Z"

            # Verify call was made correctly
            call_args = mock_request.call_args
            assert call_args[0][0] == mock_braze_context.http_client
            assert call_args[0][1] == mock_braze_context.base_url
            assert call_args[0][2] == "templates/email/info"
            params = call_args[0][3]
            assert params["email_template_id"] == "template_12345"

    @pytest.mark.asyncio
    async def test_success_response_with_minimal_data(
        self, mock_context, mock_braze_context, sample_email_template_info_minimal_data
    ):
        """Test successful email template info retrieval with minimal data."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.templates.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.templates.make_request",
                return_value=SuccessResponse(
                    data=sample_email_template_info_minimal_data, headers={}
                ),
            ),
        ):
            result = await get_email_template_info(mock_context, "template_minimal")

            assert isinstance(result, EmailTemplateInfo)
            assert result.email_template_id == "template_minimal"
            assert result.template_name == "Minimal Template"
            assert result.description == "A minimal template"
            assert result.subject == "Test Subject"
            assert result.preheader is None
            assert result.body is None
            assert result.plaintext_body is None
            assert result.should_inline_css is None
            assert result.tags == ["test"]

    @pytest.mark.asyncio
    async def test_api_error_response(self, mock_context, mock_braze_context):
        """Test handling of API error response."""
        from braze_mcp.utils.http import FailureResponse

        error_data = {"error": "Invalid email template ID"}

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
            result = await get_email_template_info(mock_context, "invalid_template")

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
            result = await get_email_template_info(mock_context, "template_12345")

            # Should return raw dict when pydantic parsing fails
            assert isinstance(result, dict)
            assert result == invalid_data

    @pytest.mark.asyncio
    async def test_unexpected_response_type(self, mock_context, mock_braze_context):
        """Test email template info handles unexpected response type"""
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
            result = await get_email_template_info(mock_context, "template_12345")

            assert isinstance(result, dict)
            assert "error" in result
            # Check that we get a standardized error response
            assert result["success"] is False
            assert result["error"]["error_type"] == "unexpected_error"
            mock_logger.assert_called_once_with(
                f"Unexpected response type: {type(unexpected_response)}"
            )
