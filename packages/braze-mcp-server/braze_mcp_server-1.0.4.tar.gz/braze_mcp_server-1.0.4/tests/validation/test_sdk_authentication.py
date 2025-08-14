"""Real API validation tests for SDK authentication tools."""

import pytest

from braze_mcp.tools.sdk_authentication import get_sdk_authentication_keys


@pytest.mark.real_api
class TestSDKAuthenticationRealAPI:
    """Real API tests for SDK authentication tools."""

    @pytest.mark.asyncio
    async def test_sdk_auth_with_invalid_app_id(self, real_context, validation_helper):
        """Test SDK authentication with invalid app ID."""
        invalid_app_id = "invalid_app_id_12345"
        result = await get_sdk_authentication_keys(real_context, invalid_app_id)

        # Should return error for invalid app ID
        validation_helper.assert_error_response(result, "for invalid app ID")
