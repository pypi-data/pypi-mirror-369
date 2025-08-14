from unittest.mock import patch

import pytest

from braze_mcp.models import PreferenceCenterDetails, PreferenceCentersResponse
from braze_mcp.tools.preference_centers import get_preference_center_details, get_preference_centers


@pytest.fixture
def sample_preference_centers_data():
    """Sample data for preference centers endpoint."""
    return {
        "preference_centers": [
            {
                "name": "My Preference Center 1",
                "preference_center_api_id": "preference_center_api_id_1",
                "created_at": "2022-08-17T15:46:10Z",
                "updated_at": "2022-08-17T15:46:10Z",
            },
            {
                "name": "My Preference Center 2",
                "preference_center_api_id": "preference_center_api_id_2",
                "created_at": "2022-08-19T11:13:06Z",
                "updated_at": "2022-08-19T11:13:06Z",
            },
            {
                "name": "My Preference Center 3",
                "preference_center_api_id": "preference_center_api_id_3",
                "created_at": "2022-08-19T11:30:50Z",
                "updated_at": "2022-08-19T11:30:50Z",
            },
            {
                "name": "My Preference Center 4",
                "preference_center_api_id": "preference_center_api_id_4",
                "created_at": "2022-09-13T20:41:34Z",
                "updated_at": "2022-09-13T20:41:34Z",
            },
        ]
    }


@pytest.fixture
def empty_preference_centers_data():
    """Sample data for empty preference centers response."""
    return {"preference_centers": []}


@pytest.fixture
def sample_preference_center_details_data():
    """Sample data for preference center details endpoint."""
    return {
        "name": "My Preference Center",
        "preference_center_api_id": "preference_center_api_id_123",
        "created_at": "2022-08-17T15:46:10Z",
        "updated_at": "2022-08-17T15:46:10Z",
        "preference_center_title": "Example preference center title",
        "preference_center_page_html": "<html><body>HTML for preference center here</body></html>",
        "confirmation_page_html": "<html><body>HTML for confirmation page here</body></html>",
        "redirect_page_html": None,
        "preference_center_options": {
            "meta-viewport-content": "width=device-width, initial-scale=2"
        },
        "state": "active",
    }


class TestGetPreferenceCenters:
    """Test get_preference_centers function"""

    @pytest.mark.asyncio
    async def test_success_response_with_data(
        self, mock_context, mock_braze_context, sample_preference_centers_data
    ):
        """Test successful preference centers retrieval with comprehensive pydantic model validation."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.preference_centers.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.preference_centers.make_request",
                return_value=SuccessResponse(data=sample_preference_centers_data, headers={}),
            ) as mock_request,
        ):
            result = await get_preference_centers(mock_context)

            # Validate pydantic model structure
            assert isinstance(result, PreferenceCentersResponse)
            assert hasattr(result, "preference_centers")

            # Validate preference centers structure
            assert len(result.preference_centers) == 4
            assert isinstance(result.preference_centers, list)

            # Verify request parameters
            call_args = mock_request.call_args
            assert call_args[0][2] == "preference_center/v1/list"
            assert call_args[0][0] == mock_braze_context.http_client
            assert call_args[0][1] == mock_braze_context.base_url
            # Verify no parameters are passed (empty dict)
            assert call_args[0][3] == {}

    @pytest.mark.asyncio
    async def test_success_response_empty_list(
        self, mock_context, mock_braze_context, empty_preference_centers_data
    ):
        """Test successful preference centers retrieval with empty list."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.preference_centers.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.preference_centers.make_request",
                return_value=SuccessResponse(data=empty_preference_centers_data, headers={}),
            ) as mock_request,
        ):
            result = await get_preference_centers(mock_context)

            # Validate pydantic model structure
            assert isinstance(result, PreferenceCentersResponse)
            assert hasattr(result, "preference_centers")
            assert isinstance(result.preference_centers, list)
            assert len(result.preference_centers) == 0

            # Verify request was made correctly
            call_args = mock_request.call_args
            assert call_args[0][2] == "preference_center/v1/list"
            assert call_args[0][3] == {}

    @pytest.mark.asyncio
    async def test_error_response(self, mock_context, mock_braze_context):
        """Test preference centers error handling."""
        from braze_mcp.utils.http import FailureResponse

        with (
            patch(
                "braze_mcp.tools.preference_centers.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.preference_centers.make_request",
                return_value=FailureResponse(
                    data={"error": "Unauthorized"}, error=Exception("API Error")
                ),
            ),
        ):
            result = await get_preference_centers(mock_context)

            # Should return error dict, not pydantic model
            assert isinstance(result, dict)
            assert "error" in result
            assert result["error"] == "Unauthorized"

    @pytest.mark.asyncio
    async def test_parsing_failure_fallback(self, mock_context, mock_braze_context):
        """Test that malformed response falls back to raw dict."""
        from braze_mcp.utils.http import SuccessResponse

        # Invalid response structure that will fail pydantic parsing
        invalid_data = {"invalid_field": "should cause parsing failure"}

        with (
            patch(
                "braze_mcp.tools.preference_centers.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.preference_centers.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ),
        ):
            result = await get_preference_centers(mock_context)

            # Should return raw dict when pydantic parsing fails
            assert isinstance(result, dict)
            assert result == invalid_data


class TestGetPreferenceCenterDetails:
    """Test get_preference_center_details function"""

    @pytest.mark.asyncio
    async def test_success_response_with_data(
        self, mock_context, mock_braze_context, sample_preference_center_details_data
    ):
        """Test successful preference center details retrieval with comprehensive pydantic model validation."""
        from braze_mcp.utils.http import SuccessResponse

        preference_center_id = "preference_center_api_id_123"

        with (
            patch(
                "braze_mcp.tools.preference_centers.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.preference_centers.make_request",
                return_value=SuccessResponse(
                    data=sample_preference_center_details_data, headers={}
                ),
            ) as mock_request,
        ):
            result = await get_preference_center_details(mock_context, preference_center_id)

            # Validate pydantic model structure
            assert isinstance(result, PreferenceCenterDetails)

            # Validate specific values
            assert result.name == "My Preference Center"
            assert result.preference_center_api_id == "preference_center_api_id_123"
            assert result.created_at == "2022-08-17T15:46:10Z"
            assert result.updated_at == "2022-08-17T15:46:10Z"
            assert result.preference_center_title == "Example preference center title"
            assert result.state == "active"
            assert result.redirect_page_html is None

            # Validate HTML content exists
            assert "<html>" in result.preference_center_page_html
            assert "<html>" in result.confirmation_page_html

            # Validate options structure
            assert isinstance(result.preference_center_options, dict)
            assert "meta-viewport-content" in result.preference_center_options
            assert (
                result.preference_center_options["meta-viewport-content"]
                == "width=device-width, initial-scale=2"
            )

            # Verify request parameters
            call_args = mock_request.call_args
            assert call_args[0][2] == f"preference_center/v1/{preference_center_id}"
            assert call_args[0][0] == mock_braze_context.http_client
            assert call_args[0][1] == mock_braze_context.base_url
            # Verify no additional parameters are passed
            assert call_args[0][3] == {}

    @pytest.mark.asyncio
    async def test_error_response(self, mock_context, mock_braze_context):
        """Test preference center details error handling."""
        from braze_mcp.utils.http import FailureResponse

        preference_center_id = "invalid_id"

        with (
            patch(
                "braze_mcp.tools.preference_centers.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.preference_centers.make_request",
                return_value=FailureResponse(
                    data={"error": "Preference center not found"}, error=Exception("Not Found")
                ),
            ),
        ):
            result = await get_preference_center_details(mock_context, preference_center_id)

            # Should return error dict, not pydantic model
            assert isinstance(result, dict)
            assert "error" in result
            assert result["error"] == "Preference center not found"

    @pytest.mark.asyncio
    async def test_parsing_failure_fallback(self, mock_context, mock_braze_context):
        """Test that malformed response falls back to raw dict."""
        from braze_mcp.utils.http import SuccessResponse

        # Invalid response structure that will fail pydantic parsing
        invalid_data = {"invalid_field": "missing required fields"}

        with (
            patch(
                "braze_mcp.tools.preference_centers.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.preference_centers.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ),
        ):
            result = await get_preference_center_details(mock_context, "test_id")

            # Should return raw dict when pydantic parsing fails
            assert isinstance(result, dict)
            assert result == invalid_data
