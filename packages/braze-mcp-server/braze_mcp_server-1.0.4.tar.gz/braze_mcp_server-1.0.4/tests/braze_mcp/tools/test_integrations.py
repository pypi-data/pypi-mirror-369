from unittest.mock import patch

import pytest

from braze_mcp.tools.integrations import get_integration_job_sync_status, list_integrations


@pytest.fixture
def sample_integrations_data():
    """Sample data for list integrations endpoint."""
    return {
        "results": [
            {
                "integration_id": "12345678-1234-1234-1234-123456789abc",
                "app_group_id": "87654321-4321-4321-4321-cba987654321",
                "integration_name": "Test Integration",
                "integration_type": "snowflake",
                "integration_status": "active",
                "contact_emails": "test@example.com",
                "last_updated_at": "2024-01-15T10:30:00Z",
                "warehouse_type": "snowflake",
                "last_job_start_time": "2024-01-15T09:45:00Z",
                "last_job_status": "success",
                "next_scheduled_run": "2024-01-16T09:45:00Z",
            }
        ],
        "message": "success",
    }


@pytest.fixture
def sample_job_sync_status_data():
    """Sample data for job sync status endpoint."""
    return {
        "results": [
            {
                "job_status": "success",
                "sync_start_time": "2024-01-15T09:45:00Z",
                "sync_finish_time": "2024-01-15T10:30:00Z",
                "last_timestamp_synced": "2024-01-15T09:44:59Z",
                "rows_synced": 1000,
                "rows_failed_with_errors": 0,
            }
        ],
        "message": "success",
    }


class TestListIntegrations:
    """Test list_integrations functionality."""

    @pytest.mark.asyncio
    async def test_list_integrations_success_with_data(
        self, mock_context, mock_braze_context, sample_integrations_data
    ):
        """Test successful list integrations with comprehensive pydantic model validation."""
        from braze_mcp.models import IntegrationsListResponse
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.integrations.get_braze_context", return_value=mock_braze_context
            ),
            patch(
                "braze_mcp.tools.integrations.make_request",
                return_value=SuccessResponse(data=sample_integrations_data, headers={}),
            ) as mock_request,
        ):
            result = await list_integrations(mock_context)

            # Validate pydantic model structure
            assert isinstance(result, IntegrationsListResponse)
            assert hasattr(result, "results")
            assert hasattr(result, "message")

            # Validate response message
            assert result.message == "success"
            assert isinstance(result.message, str)

            # Validate results structure
            assert len(result.results) == 1
            assert isinstance(result.results, list)

            # Validate integration model attributes
            integration = result.results[0]
            required_attrs = [
                "integration_id",
                "app_group_id",
                "integration_name",
                "integration_type",
                "integration_status",
                "contact_emails",
                "last_updated_at",
                "warehouse_type",
                "last_job_start_time",
                "last_job_status",
                "next_scheduled_run",
            ]

            for attr in required_attrs:
                assert hasattr(integration, attr), f"Integration missing required attribute: {attr}"
                assert getattr(integration, attr) is not None, (
                    f"Integration attribute {attr} is None"
                )

            # Validate specific values
            assert integration.integration_id == "12345678-1234-1234-1234-123456789abc"
            assert integration.integration_name == "Test Integration"
            assert integration.integration_type == "snowflake"
            assert integration.integration_status == "active"
            assert integration.warehouse_type == "snowflake"
            assert integration.last_job_status == "success"

            # Verify request parameters
            call_args = mock_request.call_args
            assert call_args[0][2] == "cdi/integrations"
            assert call_args[0][0] == mock_braze_context.http_client
            assert call_args[0][1] == mock_braze_context.base_url

    @pytest.mark.asyncio
    async def test_list_integrations_success_with_cursor(self, mock_context, mock_braze_context):
        """Test list integrations with cursor parameter."""
        from braze_mcp.models import IntegrationsListResponse
        from braze_mcp.utils.http import SuccessResponse

        cursor = "test_cursor"

        with (
            patch(
                "braze_mcp.tools.integrations.get_braze_context", return_value=mock_braze_context
            ),
            patch(
                "braze_mcp.tools.integrations.make_request",
                return_value=SuccessResponse(
                    data={"results": [], "message": "success"}, headers={}
                ),
            ) as mock_request,
        ):
            result = await list_integrations(mock_context, cursor=cursor)

            # Validate pydantic model
            assert isinstance(result, IntegrationsListResponse)
            assert hasattr(result, "results")
            assert hasattr(result, "message")
            assert result.message == "success"
            assert isinstance(result.results, list)
            assert len(result.results) == 0

            # Verify cursor was passed in params
            call_args = mock_request.call_args
            params = call_args[0][3]
            assert params["cursor"] == cursor

    @pytest.mark.asyncio
    async def test_list_integrations_error_response(self, mock_context, mock_braze_context):
        """Test list integrations error handling."""
        from braze_mcp.utils.http import FailureResponse

        with (
            patch(
                "braze_mcp.tools.integrations.get_braze_context", return_value=mock_braze_context
            ),
            patch(
                "braze_mcp.tools.integrations.make_request",
                return_value=FailureResponse(
                    data={"error": "Authentication failed"}, error=Exception("API Error")
                ),
            ),
        ):
            result = await list_integrations(mock_context)

            # Should return error dict, not pydantic model
            assert isinstance(result, dict)
            assert "error" in result
            assert result["error"] == "Authentication failed"


class TestJobSyncStatus:
    """Test integration job sync status functionality."""

    @pytest.mark.asyncio
    async def test_job_sync_status_success_with_data(
        self, mock_context, mock_braze_context, sample_job_sync_status_data
    ):
        """Test successful job sync status with comprehensive pydantic model validation."""
        from braze_mcp.models import JobSyncStatusResponse
        from braze_mcp.utils.http import SuccessResponse

        integration_id = "test-id"

        with (
            patch(
                "braze_mcp.tools.integrations.get_braze_context", return_value=mock_braze_context
            ),
            patch(
                "braze_mcp.tools.integrations.make_request",
                return_value=SuccessResponse(data=sample_job_sync_status_data, headers={}),
            ) as mock_request,
        ):
            result = await get_integration_job_sync_status(mock_context, integration_id)

            # Validate pydantic model structure
            assert isinstance(result, JobSyncStatusResponse)
            assert hasattr(result, "results")
            assert hasattr(result, "message")

            # Validate response message
            assert result.message == "success"
            assert isinstance(result.message, str)

            # Validate results structure
            assert len(result.results) == 1
            assert isinstance(result.results, list)

            # Validate job sync status model attributes
            job_status = result.results[0]
            required_attrs = [
                "job_status",
                "sync_start_time",
                "sync_finish_time",
                "last_timestamp_synced",
                "rows_synced",
                "rows_failed_with_errors",
            ]

            for attr in required_attrs:
                assert hasattr(job_status, attr), (
                    f"JobSyncStatus missing required attribute: {attr}"
                )
                assert getattr(job_status, attr) is not None, (
                    f"JobSyncStatus attribute {attr} is None"
                )

            # Validate specific values and types
            assert job_status.job_status == "success"
            assert isinstance(job_status.job_status, str)
            assert job_status.sync_start_time == "2024-01-15T09:45:00Z"
            assert job_status.sync_finish_time == "2024-01-15T10:30:00Z"
            assert job_status.last_timestamp_synced == "2024-01-15T09:44:59Z"
            assert job_status.rows_synced == 1000
            assert isinstance(job_status.rows_synced, int)
            assert job_status.rows_failed_with_errors == 0
            assert isinstance(job_status.rows_failed_with_errors, int)

            # Verify request parameters
            call_args = mock_request.call_args
            assert call_args[0][2] == "cdi/integrations/test-id/job_sync_status"
            # integration_id is part of the URL path, not the params
            assert "test-id" in call_args[0][2]

    @pytest.mark.asyncio
    async def test_job_sync_status_error_response(self, mock_context, mock_braze_context):
        """Test job sync status error handling."""
        from braze_mcp.utils.http import FailureResponse

        integration_id = "invalid-id"

        with (
            patch(
                "braze_mcp.tools.integrations.get_braze_context", return_value=mock_braze_context
            ),
            patch(
                "braze_mcp.tools.integrations.make_request",
                return_value=FailureResponse(
                    data={"error": "Integration not found"}, error=Exception("API Error")
                ),
            ),
        ):
            result = await get_integration_job_sync_status(mock_context, integration_id)

            # Should return error dict, not pydantic model
            assert isinstance(result, dict)
            assert "error" in result
            assert result["error"] == "Integration not found"
