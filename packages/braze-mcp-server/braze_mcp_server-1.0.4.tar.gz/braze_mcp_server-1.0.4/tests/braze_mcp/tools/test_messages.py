from unittest.mock import patch

import pytest

from braze_mcp.models import ScheduledBroadcastsResponse
from braze_mcp.tools.messages import get_scheduled_broadcasts


@pytest.fixture
def sample_scheduled_broadcasts_response():
    """Sample scheduled broadcasts API response"""
    return {
        "scheduled_broadcasts": [
            {
                "name": "Test Campaign",
                "id": "campaign_123",
                "type": "Campaign",
                "tags": ["test"],
                "next_send_time": "2024-02-01T10:00:00Z",
                "schedule_type": "local_time_zones",
            }
        ]
    }


class TestGetScheduledBroadcasts:
    """Test get_scheduled_broadcasts function"""

    @pytest.mark.asyncio
    async def test_success_response(
        self, mock_context, mock_braze_context, sample_scheduled_broadcasts_response
    ):
        """Test successful scheduled broadcasts retrieval."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch("braze_mcp.tools.messages.get_braze_context", return_value=mock_braze_context),
            patch(
                "braze_mcp.tools.messages.make_request",
                return_value=SuccessResponse(data=sample_scheduled_broadcasts_response, headers={}),
            ) as mock_request,
        ):
            result = await get_scheduled_broadcasts(mock_context, end_time="2024-02-10T00:00:00Z")

            assert isinstance(result, ScheduledBroadcastsResponse)
            assert len(result.scheduled_broadcasts) == 1

            broadcast = result.scheduled_broadcasts[0]
            assert broadcast.name == "Test Campaign"
            assert broadcast.type == "Campaign"

            # Verify request parameters
            call_args = mock_request.call_args
            assert call_args[0][2] == "messages/scheduled_broadcasts"
            assert call_args[0][3]["end_time"] == "2024-02-10T00:00:00Z"

    @pytest.mark.asyncio
    async def test_error_response(self, mock_context, mock_braze_context):
        """Test error response handling."""
        from braze_mcp.utils.http import FailureResponse

        with (
            patch("braze_mcp.tools.messages.get_braze_context", return_value=mock_braze_context),
            patch(
                "braze_mcp.tools.messages.make_request",
                return_value=FailureResponse(
                    data={"error": "Invalid format"}, error=Exception("Invalid format")
                ),
            ),
        ):
            result = await get_scheduled_broadcasts(mock_context, end_time="invalid")

            assert isinstance(result, dict)
            assert "error" in result
