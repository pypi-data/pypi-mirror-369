"""Real API validation tests for preference centers tools."""

from datetime import datetime

import pytest

from braze_mcp.models.preference_centers import PreferenceCenterDetails, PreferenceCentersResponse
from braze_mcp.tools.preference_centers import get_preference_center_details, get_preference_centers


@pytest.mark.real_api
class TestPreferenceCentersRealAPI:
    """Real API tests for preference centers tools."""

    @pytest.mark.asyncio
    async def test_get_preference_centers_basic(self, real_context):
        """Test get_preference_centers against real Braze API."""
        result = await get_preference_centers(real_context)

        # Validate return type is Pydantic model
        assert isinstance(result, PreferenceCentersResponse), (
            f"Expected PreferenceCentersResponse, got {type(result)}"
        )

        # Validate response structure (Pydantic model)
        assert hasattr(result, "preference_centers"), (
            "Response should have preference_centers attribute"
        )

        # Validate data types
        assert isinstance(result.preference_centers, list), "Preference centers should be a list"

        # If preference centers exist, validate structure
        if result.preference_centers:
            center = result.preference_centers[0]
            assert hasattr(center, "name"), "Preference center should have name attribute"
            assert hasattr(center, "preference_center_api_id"), (
                "Preference center should have preference_center_api_id attribute"
            )
            assert hasattr(center, "created_at"), (
                "Preference center should have created_at attribute"
            )
            assert hasattr(center, "updated_at"), (
                "Preference center should have updated_at attribute"
            )

            # Validate attribute types
            assert isinstance(center.name, str), "Name should be a string"
            assert isinstance(center.preference_center_api_id, str), "API ID should be a string"
            assert isinstance(center.created_at, str), "Created at should be a string"
            assert isinstance(center.updated_at, str), "Updated at should be a string"

            try:
                created_dt = datetime.fromisoformat(center.created_at)
                assert isinstance(created_dt, datetime), (
                    "Created at should parse to a datetime object"
                )
            except ValueError as e:
                pytest.fail(
                    f"Created at timestamp '{center.created_at}' is not valid ISO 8601: {e}"
                )

            try:
                updated_dt = datetime.fromisoformat(center.updated_at)
                assert isinstance(updated_dt, datetime), (
                    "Updated at should parse to a datetime object"
                )
            except ValueError as e:
                pytest.fail(
                    f"Updated at timestamp '{center.updated_at}' is not valid ISO 8601: {e}"
                )

            # Validate non-empty strings
            assert len(center.name.strip()) > 0, "Name should not be empty"
            assert len(center.preference_center_api_id.strip()) > 0, "API ID should not be empty"

    @pytest.mark.asyncio
    async def test_get_preference_center_details_basic(self, real_context):
        """Test get_preference_center_details against real Braze API."""
        # First get the list to find a valid preference center ID
        centers_result = await get_preference_centers(real_context)

        # Skip if no preference centers exist
        if not centers_result.preference_centers:
            pytest.skip("No preference centers available for testing")

        # Use the first preference center ID for detailed lookup
        test_center_id = centers_result.preference_centers[0].preference_center_api_id

        result = await get_preference_center_details(real_context, test_center_id)

        # Validate return type is Pydantic model
        assert isinstance(result, PreferenceCenterDetails), (
            f"Expected PreferenceCenterDetails, got {type(result)}"
        )

        # Validate response structure (Pydantic model)
        assert hasattr(result, "name"), "Response should have name attribute"
        assert hasattr(result, "preference_center_api_id"), (
            "Response should have preference_center_api_id attribute"
        )
        assert hasattr(result, "created_at"), "Response should have created_at attribute"
        assert hasattr(result, "updated_at"), "Response should have updated_at attribute"
        assert hasattr(result, "preference_center_title"), (
            "Response should have preference_center_title attribute"
        )
        assert hasattr(result, "preference_center_page_html"), (
            "Response should have preference_center_page_html attribute"
        )
        assert hasattr(result, "confirmation_page_html"), (
            "Response should have confirmation_page_html attribute"
        )
        assert hasattr(result, "redirect_page_html"), (
            "Response should have redirect_page_html attribute"
        )
        assert hasattr(result, "preference_center_options"), (
            "Response should have preference_center_options attribute"
        )
        assert hasattr(result, "state"), "Response should have state attribute"

        # Validate attribute types
        assert isinstance(result.name, str), "Name should be a string"
        assert isinstance(result.preference_center_api_id, str), "API ID should be a string"
        assert isinstance(result.created_at, str), "Created at should be a string"
        assert isinstance(result.updated_at, str), "Updated at should be a string"
        assert isinstance(result.preference_center_title, str), "Title should be a string"
        assert isinstance(result.preference_center_page_html, str), "Page HTML should be a string"
        assert isinstance(result.confirmation_page_html, str), (
            "Confirmation HTML should be a string"
        )
        assert result.redirect_page_html is None or isinstance(result.redirect_page_html, str), (
            "Redirect HTML should be string or None"
        )
        if result.preference_center_options:
            assert isinstance(result.preference_center_options, dict), (
                "Options should be a dictionary"
            )
        assert isinstance(result.state, str), "State should be a string"

        try:
            created_dt = datetime.fromisoformat(result.created_at)
            assert isinstance(created_dt, datetime), "Created at should parse to a datetime object"
        except ValueError as e:
            pytest.fail(f"Created at timestamp '{result.created_at}' is not valid ISO 8601: {e}")

        try:
            updated_dt = datetime.fromisoformat(result.updated_at)
            assert isinstance(updated_dt, datetime), "Updated at should parse to a datetime object"
        except ValueError as e:
            pytest.fail(f"Updated at timestamp '{result.updated_at}' is not valid ISO 8601: {e}")

        # Validate non-empty strings
        assert len(result.name.strip()) > 0, "Name should not be empty"
        assert len(result.preference_center_api_id.strip()) > 0, "API ID should not be empty"
        assert len(result.preference_center_title.strip()) > 0, "Title should not be empty"
        assert len(result.preference_center_page_html.strip()) > 0, "Page HTML should not be empty"
        assert len(result.confirmation_page_html.strip()) > 0, (
            "Confirmation HTML should not be empty"
        )
        assert result.state in ["active", "draft"], "State should be active or draft"

        # Validate that we got the correct preference center
        assert result.preference_center_api_id == test_center_id, (
            "Should return details for the requested preference center"
        )
