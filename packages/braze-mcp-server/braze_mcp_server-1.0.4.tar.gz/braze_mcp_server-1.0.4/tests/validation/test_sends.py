"""Real API validation tests for sends tools."""

import pytest

from braze_mcp.models.send_dataseries import SendDataSeriesResponse
from braze_mcp.tools.sends import get_send_data_series


@pytest.mark.real_api
class TestSendsRealAPI:
    """Real API tests for sends tools."""

    @pytest.mark.asyncio
    async def test_get_send_data_series_basic(self, real_context):
        """Test get_send_data_series against real Braze API."""
        result = await get_send_data_series(
            real_context,
            campaign_id="1f815242-45d4-4470-963a-f6acdeab290d",  # Hardcoded campaign and send id for testing associated with a test API key
            send_id="c6242f8f-1b3c-46b8-b85e-66148e9ab7eb",
            length=7,
        )

        # Validate return type is Pydantic model
        assert isinstance(result, SendDataSeriesResponse), (
            f"Expected SendDataSeriesResponse, got {type(result)}"
        )

        # Validate response structure (Pydantic model)
        assert hasattr(result, "data"), "Response should have data attribute"
        assert hasattr(result, "message"), "Response should have message attribute"

        # Validate data types
        assert isinstance(result.data, list), "Data should be a list"
        assert isinstance(result.message, str), "Message should be a string"
