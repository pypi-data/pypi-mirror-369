from unittest.mock import patch

import pytest

from braze_mcp.models import SDKAuthenticationKeysResponse
from braze_mcp.tools.sdk_authentication import get_sdk_authentication_keys


@pytest.fixture
def sample_sdk_authentication_keys_data():
    return {
        "keys": [
            {
                "id": "test-key-id",
                "rsa_public_key": "-----BEGIN PUBLIC KEY-----\nTEST_KEY\n-----END PUBLIC KEY-----",
                "description": "Test SDK Key",
                "is_primary": True,
            }
        ]
    }


class TestGetSDKAuthenticationKeys:
    """Test get_sdk_authentication_keys function"""

    @pytest.mark.asyncio
    async def test_success_response(
        self, mock_context, mock_braze_context, sample_sdk_authentication_keys_data
    ):
        """Test successful retrieval of SDK authentication keys"""
        from braze_mcp.utils.http import SuccessResponse

        app_id = "test-app-id"

        with (
            patch(
                "braze_mcp.tools.sdk_authentication.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.sdk_authentication.make_request",
                return_value=SuccessResponse(data=sample_sdk_authentication_keys_data, headers={}),
            ) as mock_request,
        ):
            result = await get_sdk_authentication_keys(mock_context, app_id)

            assert isinstance(result, SDKAuthenticationKeysResponse)
            assert len(result.keys) == 1

            key = result.keys[0]
            assert key.id == "test-key-id"
            assert key.is_primary is True
            assert "BEGIN PUBLIC KEY" in key.rsa_public_key

            # Verify API call
            call_args = mock_request.call_args
            assert call_args[0][2] == "app_group/sdk_authentication/keys"
            assert call_args[0][3]["app_id"] == app_id

    @pytest.mark.asyncio
    async def test_error_response(self, mock_context, mock_braze_context):
        """Test handling of API errors"""
        from braze_mcp.utils.http import FailureResponse

        app_id = "test-app-id"

        with (
            patch(
                "braze_mcp.tools.sdk_authentication.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.sdk_authentication.make_request",
                return_value=FailureResponse(
                    data={"error": "Invalid API key"}, error=Exception("Unauthorized")
                ),
            ),
        ):
            result = await get_sdk_authentication_keys(mock_context, app_id)

            assert isinstance(result, dict)
            assert "error" in result
