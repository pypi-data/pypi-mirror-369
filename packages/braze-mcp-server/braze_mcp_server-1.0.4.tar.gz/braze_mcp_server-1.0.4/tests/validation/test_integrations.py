"""Real API validation tests for CDI integration tools."""

import pytest

from braze_mcp.models.integrations import IntegrationsListResponse, JobSyncStatusResponse
from braze_mcp.tools.integrations import get_integration_job_sync_status, list_integrations


@pytest.mark.real_api
class TestIntegrationsRealAPI:
    """Real API tests for CDI integration tools."""

    @pytest.mark.asyncio
    async def test_list_integrations(self, real_context, validation_helper):
        """Test list_integrations endpoint."""
        result = await list_integrations(real_context)

        # Validate Pydantic model response
        validation_helper.assert_pydantic_response(result, IntegrationsListResponse)
        validation_helper.assert_string_field(result, "message")
        validation_helper.assert_list_field(result, "results")

        integration_results = result.results
        assert len(integration_results) > 0, "Should have at least one integration"
        integration = integration_results[0]

        # Core integration fields validation
        required_fields = [
            "integration_id",
            "integration_name",
            "integration_type",
            "integration_status",
            "contact_emails",
            "warehouse_type",
        ]
        for field in required_fields:
            field_value = getattr(integration, field, None)
            assert field_value is not None, f"Integration should have {field}: got {field_value}"

    @pytest.mark.asyncio
    async def test_list_integrations_pagination(self, real_context, validation_helper):
        """Test list_integrations pagination functionality."""
        # Get initial list to check for pagination cursor
        first_result = await list_integrations(real_context)
        cursor = getattr(first_result, "next_cursor", None)

        # Test pagination with cursor
        result = await list_integrations(real_context, cursor=cursor)
        validation_helper.assert_pydantic_response(result, IntegrationsListResponse)

    @pytest.mark.asyncio
    async def test_get_integration_job_sync_status_valid_id(self, real_context, validation_helper):
        """Test get_integration_job_sync_status with valid integration ID from list."""
        # First get a list of integrations to extract a valid ID
        integrations_result = await list_integrations(real_context)
        validation_helper.assert_pydantic_response(integrations_result, IntegrationsListResponse)

        assert len(integrations_result.results) > 0, "Need at least one integration for testing"
        valid_integration_id = integrations_result.results[0].integration_id

        # Test with valid integration ID
        result = await get_integration_job_sync_status(real_context, valid_integration_id)

        # Should return successful JobSyncStatusResponse
        validation_helper.assert_pydantic_response(result, JobSyncStatusResponse)
        validation_helper.assert_string_field(result, "message")
        validation_helper.assert_list_field(result, "results")

    @pytest.mark.asyncio
    async def test_error_handling_invalid_integration_id(self, real_context, validation_helper):
        """Test error handling with invalid integration ID."""
        invalid_id = "00000000-0000-0000-0000-000000000000"
        result = await get_integration_job_sync_status(real_context, invalid_id)

        # Should return error response for invalid ID
        validation_helper.assert_error_response(result, "for invalid integration ID")
