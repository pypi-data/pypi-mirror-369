"""Real API validation tests for sessions tools."""

import pytest

from braze_mcp.models.sessions import SessionDataSeriesResponse
from braze_mcp.tools.sessions import get_session_data_series


@pytest.mark.real_api
class TestSessionsRealAPI:
    """Real API tests for sessions tools."""

    @pytest.mark.asyncio
    async def test_get_session_data_series_basic(self, real_context):
        """Test get_session_data_series against real Braze API."""
        result = await get_session_data_series(real_context, length=7)

        # Validate return type is Pydantic model
        assert isinstance(result, SessionDataSeriesResponse), (
            f"Expected SessionDataSeriesResponse, got {type(result)}"
        )

        # Validate response structure (Pydantic model)
        assert hasattr(result, "data"), "Response should have data attribute"
        assert hasattr(result, "message"), "Response should have message attribute"

        # Validate data types
        assert isinstance(result.data, list), "Data should be a list"
        assert isinstance(result.message, str), "Message should be a string"

    @pytest.mark.asyncio
    async def test_get_session_data_series_with_parameters(self, real_context):
        """Test get_session_data_series with parameters against real Braze API."""
        result = await get_session_data_series(real_context, length=7, unit="day")

        # Validate return type is Pydantic model
        assert isinstance(result, SessionDataSeriesResponse), (
            f"Expected SessionDataSeriesResponse, got {type(result)}"
        )

        # Should still get valid response
        assert hasattr(result, "data"), "Response should have data attribute"
        assert hasattr(result, "message"), "Response should have message attribute"
