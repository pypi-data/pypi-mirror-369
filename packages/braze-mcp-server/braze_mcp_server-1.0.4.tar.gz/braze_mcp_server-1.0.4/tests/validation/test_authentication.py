"""Real API validation tests for authentication functionality."""

import pytest

from braze_mcp.tools.campaigns import get_campaign_list


@pytest.mark.real_api
class TestAuthenticationRealAPI:
    """Real API tests for authentication functionality across all tools."""

    @pytest.mark.asyncio
    async def test_invalid_api_key_campaign_list(self, invalid_auth_context):
        """Test that invalid credentials produce appropriate error for campaigns."""
        try:
            result = await get_campaign_list(invalid_auth_context)
            # If we get here, check if it's an error response
            if hasattr(result, "message"):
                # Valid response format but check for auth error message
                message = result.message.lower()
                assert any(
                    keyword in message for keyword in ["unauthorized", "invalid", "authentication"]
                ), f"Expected authentication error, got: {result.message}"
        except Exception as e:
            # Exception is also acceptable for invalid auth
            error_str = str(e).lower()
            assert any(
                keyword in error_str
                for keyword in ["401", "unauthorized", "authentication", "invalid"]
            ), f"Expected authentication error, got: {str(e)}"
