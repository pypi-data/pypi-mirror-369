"""Real API validation tests for KPI tools."""

import pytest

from braze_mcp.models.kpi import DAUDataSeriesResponse, NewUsersDataSeriesResponse
from braze_mcp.tools.kpi import get_dau_data_series, get_new_users_data_series


@pytest.mark.real_api
class TestKPIRealAPI:
    """Real API tests for KPI tools."""

    @pytest.mark.asyncio
    async def test_get_dau_data_series_basic(self, real_context):
        """Test get_dau_data_series against real Braze API."""
        result = await get_dau_data_series(real_context, length=7)

        # Validate return type is Pydantic model
        assert isinstance(result, DAUDataSeriesResponse), (
            f"Expected DAUDataSeriesResponse, got {type(result)}"
        )

        # Validate response structure (Pydantic model)
        assert hasattr(result, "data"), "Response should have data attribute"
        assert hasattr(result, "message"), "Response should have message attribute"

        # Validate data types
        assert isinstance(result.data, list), "Data should be a list"
        assert isinstance(result.message, str), "Message should be a string"

    @pytest.mark.asyncio
    async def test_get_new_users_data_series_basic(self, real_context):
        """Test get_new_users_data_series against real Braze API."""
        result = await get_new_users_data_series(real_context, length=7)

        # Validate return type is Pydantic model
        assert isinstance(result, NewUsersDataSeriesResponse), (
            f"Expected NewUsersDataSeriesResponse, got {type(result)}"
        )

        # Validate response structure (Pydantic model)
        assert hasattr(result, "data"), "Response should have data attribute"
        assert hasattr(result, "message"), "Response should have message attribute"

        # Validate data types
        assert isinstance(result.data, list), "Data should be a list"
        assert isinstance(result.message, str), "Message should be a string"
