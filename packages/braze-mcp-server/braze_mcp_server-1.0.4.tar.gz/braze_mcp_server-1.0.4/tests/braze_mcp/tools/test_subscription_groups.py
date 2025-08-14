from unittest.mock import patch

import pytest

from braze_mcp.models import SubscriptionGroupsResponse, SubscriptionGroupStatusResponse
from braze_mcp.tools.subscription_groups import (
    get_subscription_group_status,
    get_user_subscription_groups,
)


@pytest.fixture
def sample_subscription_groups_data():
    """Sample data for subscription groups endpoint."""
    return {
        "message": "success",
        "total_count": 1,
        "users": [
            {
                "email": "test@example.com",
                "external_id": "test_user_123",
                "phone": "234567890",
                "subscription_groups": [
                    {
                        "channel": "email",
                        "id": "group_id_1",
                        "name": "Test Group 1",
                        "status": "Subscribed",
                    },
                    {
                        "channel": "email",
                        "id": "group_id_2",
                        "name": "Test Group 2",
                        "status": "Unsubscribed",
                    },
                    {
                        "channel": "sms",
                        "id": "group_id_3",
                        "name": "SMS Group",
                        "status": "Subscribed",
                    },
                ],
            }
        ],
    }


@pytest.fixture
def empty_subscription_groups_data():
    """Sample data for empty subscription groups response."""
    return {
        "message": "success",
        "total_count": 1,
        "users": [
            {
                "email": None,
                "external_id": "empty_user",
                "phone": None,
                "subscription_groups": [],
            }
        ],
    }


@pytest.fixture
def sample_subscription_status_data():
    """Sample data for subscription group status endpoint."""
    return {
        "message": "success",
        "status": {
            "user1": "Subscribed",
            "user2": "Unsubscribed",
            "user3": "Unknown",
        },
    }


@pytest.fixture
def empty_subscription_status_data():
    """Sample data for empty subscription group status response."""
    return {
        "message": "success",
        "status": {},
    }


class TestGetUserSubscriptionGroups:
    """Test get_user_subscription_groups function"""

    @pytest.mark.asyncio
    async def test_success_response_with_external_id(
        self, mock_context, mock_braze_context, sample_subscription_groups_data
    ):
        """Test successful subscription groups retrieval with external_id."""
        from braze_mcp.utils.http import SuccessResponse

        external_id = "test_user_123"

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=sample_subscription_groups_data, headers={}),
            ) as mock_request,
        ):
            result = await get_user_subscription_groups(mock_context, external_id=external_id)

            # Verify pydantic model parsing succeeded
            assert isinstance(result, SubscriptionGroupsResponse)

            # Validate specific values
            assert result.message == "success"
            assert result.total_count == 1
            assert len(result.users) == 1

            # Check user data
            user = result.users[0]
            assert user.email == "test@example.com"
            assert user.external_id == "test_user_123"
            assert user.phone == "234567890"
            assert len(user.subscription_groups) == 3

            # Check first subscription group
            first_group = user.subscription_groups[0]
            assert first_group.id == "group_id_1"
            assert first_group.name == "Test Group 1"
            assert first_group.channel == "email"
            assert first_group.status == "Subscribed"

            # Check second subscription group
            second_group = user.subscription_groups[1]
            assert second_group.id == "group_id_2"
            assert second_group.name == "Test Group 2"
            assert second_group.status == "Unsubscribed"

            # Verify request parameters
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[2] == "subscription/user/status"

            # Check query parameters
            params = args[3]
            assert params["external_id[]"] == external_id

    @pytest.mark.asyncio
    async def test_success_response_with_email(
        self, mock_context, mock_braze_context, sample_subscription_groups_data
    ):
        """Test successful subscription groups retrieval with email."""
        from braze_mcp.utils.http import SuccessResponse

        email = "test@example.com"

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=sample_subscription_groups_data, headers={}),
            ) as mock_request,
        ):
            result = await get_user_subscription_groups(mock_context, email=email)

            assert isinstance(result, SubscriptionGroupsResponse)
            assert result.message == "success"

            # Verify request parameters
            args, kwargs = mock_request.call_args
            params = args[3]
            assert params["email[]"] == email

    @pytest.mark.asyncio
    async def test_success_response_with_phone(
        self, mock_context, mock_braze_context, sample_subscription_groups_data
    ):
        """Test successful subscription groups retrieval with phone."""
        from braze_mcp.utils.http import SuccessResponse

        phone = "+1234567890"

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=sample_subscription_groups_data, headers={}),
            ) as mock_request,
        ):
            result = await get_user_subscription_groups(mock_context, phone=phone)

            assert isinstance(result, SubscriptionGroupsResponse)
            assert result.message == "success"

            # Verify request parameters
            args, kwargs = mock_request.call_args
            params = args[3]
            assert params["phone[]"] == phone

    @pytest.mark.asyncio
    async def test_success_response_with_multiple_external_ids(
        self, mock_context, mock_braze_context, sample_subscription_groups_data
    ):
        """Test successful subscription groups retrieval with multiple external_ids."""
        from braze_mcp.utils.http import SuccessResponse

        external_ids = ["user1", "user2", "user3"]

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=sample_subscription_groups_data, headers={}),
            ) as mock_request,
        ):
            result = await get_user_subscription_groups(mock_context, external_id=external_ids)

            assert isinstance(result, SubscriptionGroupsResponse)
            assert result.message == "success"

            # Verify request parameters for multiple external_ids
            args, kwargs = mock_request.call_args
            params = args[3]
            assert params["external_id[]"] == external_ids

    @pytest.mark.asyncio
    async def test_success_response_with_multiple_emails(
        self, mock_context, mock_braze_context, sample_subscription_groups_data
    ):
        """Test successful subscription groups retrieval with multiple emails."""
        from braze_mcp.utils.http import SuccessResponse

        emails = ["user1@example.com", "user2@example.com", "user3@example.com"]

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=sample_subscription_groups_data, headers={}),
            ) as mock_request,
        ):
            result = await get_user_subscription_groups(mock_context, email=emails)

            assert isinstance(result, SubscriptionGroupsResponse)
            assert result.message == "success"

            # Verify request parameters for multiple emails
            args, kwargs = mock_request.call_args
            params = args[3]
            assert params["email[]"] == emails

    @pytest.mark.asyncio
    async def test_success_response_with_multiple_phones(
        self, mock_context, mock_braze_context, sample_subscription_groups_data
    ):
        """Test successful subscription groups retrieval with multiple phone numbers."""
        from braze_mcp.utils.http import SuccessResponse

        phones = ["+1234567890", "+1987654321", "+1555123456"]

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=sample_subscription_groups_data, headers={}),
            ) as mock_request,
        ):
            result = await get_user_subscription_groups(mock_context, phone=phones)

            assert isinstance(result, SubscriptionGroupsResponse)
            assert result.message == "success"

            # Verify request parameters for multiple phones
            args, kwargs = mock_request.call_args
            params = args[3]
            assert params["phone[]"] == phones

    @pytest.mark.asyncio
    async def test_success_response_with_limit_and_offset(
        self, mock_context, mock_braze_context, sample_subscription_groups_data
    ):
        """Test successful subscription groups retrieval with limit and offset."""
        from braze_mcp.utils.http import SuccessResponse

        external_id = "test_user"
        limit = 50
        offset = 10

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=sample_subscription_groups_data, headers={}),
            ) as mock_request,
        ):
            result = await get_user_subscription_groups(
                mock_context, external_id=external_id, limit=limit, offset=offset
            )

            assert isinstance(result, SubscriptionGroupsResponse)
            assert result.message == "success"

            # Verify request parameters include limit and offset
            args, kwargs = mock_request.call_args
            params = args[3]
            assert params["external_id[]"] == external_id
            assert params["limit"] == limit
            assert params["offset"] == offset

    @pytest.mark.asyncio
    async def test_empty_response(
        self, mock_context, mock_braze_context, empty_subscription_groups_data
    ):
        """Test handling of empty subscription groups response."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=empty_subscription_groups_data, headers={}),
            ),
        ):
            result = await get_user_subscription_groups(mock_context, external_id="test_user")

            assert isinstance(result, SubscriptionGroupsResponse)
            assert result.message == "success"
            assert result.total_count == 1
            assert len(result.users) == 1
            assert len(result.users[0].subscription_groups) == 0

    @pytest.mark.asyncio
    async def test_validation_error_no_identifiers(self, mock_context):
        """Test validation error when no identifiers are provided."""
        with pytest.raises(
            ValueError, match="At least one of external_id, email, or phone must be provided"
        ):
            await get_user_subscription_groups(mock_context)

    @pytest.mark.asyncio
    async def test_validation_error_email_and_phone_both_provided(self, mock_context):
        """Test validation error when both email and phone are provided."""
        with pytest.raises(
            ValueError,
            match="Either an email address or a phone number should be provided, but not both",
        ):
            await get_user_subscription_groups(
                mock_context, email="test@example.com", phone="+1234567890"
            )

    @pytest.mark.asyncio
    async def test_api_error_response(self, mock_context, mock_braze_context):
        """Test handling of API error response."""
        from braze_mcp.utils.http import FailureResponse

        error_data = {"error": "Invalid API key"}

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=FailureResponse(data=error_data, error=Exception("API Error")),
            ),
        ):
            result = await get_user_subscription_groups(mock_context, external_id="test_user")

            # Should return error dict when there's an API error
            assert isinstance(result, dict)
            assert result == error_data

    @pytest.mark.asyncio
    async def test_invalid_response_format(self, mock_context, mock_braze_context):
        """Test handling of invalid response format that can't be parsed by pydantic."""
        from braze_mcp.utils.http import SuccessResponse

        invalid_data = {"invalid_field": "this doesn't match the expected schema"}

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ),
        ):
            result = await get_user_subscription_groups(mock_context, external_id="test_user")

            # Should return raw dict when pydantic parsing fails
            assert isinstance(result, dict)
            assert result == invalid_data


class TestGetSubscriptionGroupStatus:
    """Test get_subscription_group_status function"""

    @pytest.mark.asyncio
    async def test_success_response_with_external_id(
        self, mock_context, mock_braze_context, sample_subscription_status_data
    ):
        """Test successful response with external_id parameter."""
        from braze_mcp.utils.http import SuccessResponse

        subscription_group_id = "test_group_123"
        external_id = "user1"

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=sample_subscription_status_data, headers={}),
            ) as mock_request,
        ):
            result = await get_subscription_group_status(
                mock_context, subscription_group_id=subscription_group_id, external_id=external_id
            )

            # Check that the mock was called with correct parameters
            args, kwargs = mock_request.call_args
            assert args[2] == "subscription/status/get"

            # Check query parameters
            params = args[3]
            assert params["subscription_group_id"] == subscription_group_id
            assert params["external_id[]"] == external_id

            # Check return value
            assert isinstance(result, SubscriptionGroupStatusResponse)
            assert result.message == "success"
            assert result.status["user1"] == "Subscribed"
            assert result.status["user2"] == "Unsubscribed"
            assert result.status["user3"] == "Unknown"

    @pytest.mark.asyncio
    async def test_success_response_with_email(
        self, mock_context, mock_braze_context, sample_subscription_status_data
    ):
        """Test successful response with email parameter."""
        from braze_mcp.utils.http import SuccessResponse

        subscription_group_id = "test_group_123"
        email = "test@example.com"

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=sample_subscription_status_data, headers={}),
            ) as mock_request,
        ):
            result = await get_subscription_group_status(
                mock_context, subscription_group_id=subscription_group_id, email=email
            )

            # Verify request parameters
            args, kwargs = mock_request.call_args
            params = args[3]
            assert params["subscription_group_id"] == subscription_group_id
            assert params["email[]"] == email

            assert isinstance(result, SubscriptionGroupStatusResponse)
            assert result.message == "success"

    @pytest.mark.asyncio
    async def test_success_response_with_phone(
        self, mock_context, mock_braze_context, sample_subscription_status_data
    ):
        """Test successful response with phone parameter."""
        from braze_mcp.utils.http import SuccessResponse

        subscription_group_id = "test_group_123"
        phone = "+1234567890"

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=sample_subscription_status_data, headers={}),
            ) as mock_request,
        ):
            result = await get_subscription_group_status(
                mock_context, subscription_group_id=subscription_group_id, phone=phone
            )

            # Verify request parameters
            args, kwargs = mock_request.call_args
            params = args[3]
            assert params["subscription_group_id"] == subscription_group_id
            assert params["phone[]"] == phone

            assert isinstance(result, SubscriptionGroupStatusResponse)
            assert result.message == "success"

    @pytest.mark.asyncio
    async def test_success_response_with_multiple_external_ids(
        self, mock_context, mock_braze_context, sample_subscription_status_data
    ):
        """Test successful response with multiple external_ids."""
        from braze_mcp.utils.http import SuccessResponse

        subscription_group_id = "test_group_123"
        external_ids = ["user1", "user2", "user3"]

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=sample_subscription_status_data, headers={}),
            ) as mock_request,
        ):
            result = await get_subscription_group_status(
                mock_context, subscription_group_id=subscription_group_id, external_id=external_ids
            )

            # Verify request parameters
            args, kwargs = mock_request.call_args
            params = args[3]
            assert params["subscription_group_id"] == subscription_group_id
            assert params["external_id[]"] == external_ids

            assert isinstance(result, SubscriptionGroupStatusResponse)
            assert result.message == "success"

    @pytest.mark.asyncio
    async def test_empty_response(
        self, mock_context, mock_braze_context, empty_subscription_status_data
    ):
        """Test handling of empty response."""
        from braze_mcp.utils.http import SuccessResponse

        subscription_group_id = "test_group_123"
        external_id = "nonexistent_user"

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=empty_subscription_status_data, headers={}),
            ),
        ):
            result = await get_subscription_group_status(
                mock_context, subscription_group_id=subscription_group_id, external_id=external_id
            )

            assert isinstance(result, SubscriptionGroupStatusResponse)
            assert result.message == "success"
            assert len(result.status) == 0

    @pytest.mark.asyncio
    async def test_validation_error_no_identifiers(self, mock_context):
        """Test validation error when no identifiers are provided."""
        with pytest.raises(
            ValueError, match="At least one of external_id, email, or phone must be provided"
        ):
            await get_subscription_group_status(mock_context, subscription_group_id="test_group")

    @pytest.mark.asyncio
    async def test_validation_error_email_and_phone_without_external_id(self, mock_context):
        """Test validation error when both email and phone are provided without external_id."""
        with pytest.raises(
            ValueError,
            match="Either an email address or a phone number should be provided, but not both",
        ):
            await get_subscription_group_status(
                mock_context,
                subscription_group_id="test_group",
                email="test@example.com",
                phone="+1234567890",
            )

    @pytest.mark.asyncio
    async def test_api_error_response(self, mock_context, mock_braze_context):
        """Test handling of API error response."""
        from braze_mcp.utils.http import FailureResponse

        error_data = {
            "error": {
                "error_type": "http_error",
                "message": "Request failed with status code 400",
                "details": "HTTP 400",
                "operation": "request to subscription/status/get",
            },
            "success": False,
            "retryable": True,
        }

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=FailureResponse(data=error_data, error=Exception("HTTP 400")),
            ),
        ):
            result = await get_subscription_group_status(
                mock_context, subscription_group_id="invalid_group", external_id="test_user"
            )

            assert result == error_data

    @pytest.mark.asyncio
    async def test_invalid_response_format(self, mock_context, mock_braze_context):
        """Test handling of invalid response format that can't be parsed by pydantic."""
        from braze_mcp.utils.http import SuccessResponse

        invalid_data = {"invalid": "data", "missing": "required_fields"}

        with (
            patch(
                "braze_mcp.tools.subscription_groups.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.subscription_groups.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ),
        ):
            result = await get_subscription_group_status(
                mock_context, subscription_group_id="test_group", external_id="test_user"
            )

            # Should return raw dict when pydantic parsing fails
            assert isinstance(result, dict)
            assert result == invalid_data
