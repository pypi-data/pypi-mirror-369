"""Real API validation tests for subscription groups tools."""

import pytest

from braze_mcp.models.subscription_groups import (
    SubscriptionGroupsResponse,
    SubscriptionGroupStatusResponse,
)
from braze_mcp.tools.subscription_groups import (
    get_subscription_group_status,
    get_user_subscription_groups,
)
from braze_mcp.utils import get_logger

logger = get_logger(__name__)


@pytest.mark.real_api
class TestUserSubscriptionGroupsRealAPI:
    """Real API tests for subscription groups tools."""

    @pytest.mark.asyncio
    async def test_get_user_subscription_groups_with_data(self, real_context):
        """Test get_user_subscription_groups with external_id that has subscription groups."""
        result = await get_user_subscription_groups(real_context, external_id="bb")

        assert isinstance(result, SubscriptionGroupsResponse), (
            f"Expected SubscriptionGroupsResponse, got {type(result)}"
        )

        assert result.message == "success", "API call should be successful"

        assert len(result.users) > 0, "external_id 'bb' should return at least one user"

        user = result.users[0]
        assert user.external_id == "bb", "User should have the requested external_id"

        assert len(user.subscription_groups) > 0, (
            "external_id 'bb' should have at least one subscription group"
        )

        logger.info(
            f"Found {len(user.subscription_groups)} subscription groups for external_id 'bb'"
        )

    @pytest.mark.asyncio
    async def test_get_user_subscription_groups_empty(self, real_context):
        """Test get_user_subscription_groups with external_id that has no subscription groups."""
        # Test with external_id "cc" which should have no subscription groups
        result = await get_user_subscription_groups(real_context, external_id="cc")

        assert isinstance(result, SubscriptionGroupsResponse), (
            f"Expected SubscriptionGroupsResponse, got {type(result)}"
        )

        assert result.message == "success", "API call should be successful"

        assert len(result.users) == 1, "Should return exactly one user"

        user = result.users[0]
        assert user.external_id == "cc", "User should have the requested external_id"
        assert len(user.subscription_groups) == 0, (
            "external_id 'cc' should have no subscription groups"
        )

    @pytest.mark.asyncio
    async def test_get_user_subscription_groups_with_email(self, real_context):
        """Test get_user_subscription_groups with email parameter."""
        # Test with a known email
        result = await get_user_subscription_groups(real_context, email="test@example.com")

        assert isinstance(result, SubscriptionGroupsResponse)
        assert result.message == "success"

    @pytest.mark.asyncio
    async def test_get_user_subscription_groups_with_limit(self, real_context):
        """Test get_user_subscription_groups with limit parameter."""
        result = await get_user_subscription_groups(real_context, external_id=["bb", "cc"], limit=1)

        assert isinstance(result, SubscriptionGroupsResponse)
        assert result.message == "success"

        # Validate that we don't get more users than expected and that subscription groups respect limit
        assert len(result.users) == 1, "Should return only one user"

    @pytest.mark.asyncio
    async def test_get_user_subscription_groups_multiple_external_ids(self, real_context):
        """Test get_user_subscription_groups with multiple external_ids (one with data, one empty)."""
        # Test with both "bb" (has subscription groups) and "cc" (empty)
        external_ids = ["bb", "cc"]

        result = await get_user_subscription_groups(real_context, external_id=external_ids)

        assert isinstance(result, SubscriptionGroupsResponse)
        assert result.message == "success"

        assert result.total_count == 2, "Should return data for both external_ids"
        assert len(result.users) == 2, "Should return exactly 2 users"

        # Find the users by external_id
        bb_user = next((u for u in result.users if u.external_id == "bb"), None)
        cc_user = next((u for u in result.users if u.external_id == "cc"), None)

        assert bb_user is not None, "Should find user with external_id 'bb'"
        assert cc_user is not None, "Should find user with external_id 'cc'"

        assert len(bb_user.subscription_groups) > 0, "bb should have subscription groups"
        assert len(cc_user.subscription_groups) == 0, "cc should have no subscription groups"

        total_groups = sum(len(user.subscription_groups) for user in result.users)
        logger.info(
            f"Multiple external_ids returned {total_groups} total subscription groups across {len(result.users)} users"
        )

        for user in result.users:
            for group in user.subscription_groups:
                assert isinstance(group.id, str)
                assert isinstance(group.status, str)
                assert group.status in ["Subscribed", "Unsubscribed"]

    @pytest.mark.asyncio
    async def test_get_user_subscription_groups_multiple_emails(self, real_context):
        """Test get_user_subscription_groups with multiple email addresses."""
        # Test with multiple email addresses - test@example.com exists, the others do not
        emails = ["test@example.com", "another@test.com", "nonexistent@example.org"]

        result = await get_user_subscription_groups(real_context, email=emails)

        assert isinstance(result, SubscriptionGroupsResponse)
        assert result.message == "success"

        # Should return results for all provided emails (even if no subscription groups)
        logger.info(f"Multiple emails returned {result.total_count} users with subscription groups")

        # Validate any returned users and subscription groups
        for user in result.users:
            assert user.email is not None, "User should have an email when queried by email"
            assert user.email in emails, (
                f"Returned email {user.email} should be in requested emails"
            )

            # Validate subscription groups structure if any exist
            for group in user.subscription_groups:
                assert isinstance(group.id, str)
                assert isinstance(group.name, str)
                assert isinstance(group.channel, str)
                assert isinstance(group.status, str)
                assert group.status in ["Subscribed", "Unsubscribed"]

    @pytest.mark.asyncio
    async def test_get_user_subscription_groups_multiple_phones(self, real_context):
        """Test get_user_subscription_groups with multiple phone numbers."""
        phones = ["6466759783", "5166472944"]

        result = await get_user_subscription_groups(real_context, phone=phones)

        assert isinstance(result, SubscriptionGroupsResponse)
        assert result.message == "success"

        logger.info(f"Multiple phones returned {result.total_count} users with subscription groups")

        for user in result.users:
            # Note: phone might be None if user doesn't have a phone number associated
            if user.phone:
                # Phone numbers might be formatted differently than input, so just check it's a string
                assert isinstance(user.phone, str), "Phone should be a string if present"

            for group in user.subscription_groups:
                assert isinstance(group.id, str)
                assert isinstance(group.name, str)
                assert isinstance(group.channel, str)
                assert isinstance(group.status, str)
                assert group.status in ["Subscribed", "Unsubscribed"]

    @pytest.mark.asyncio
    async def test_get_user_subscription_groups_external_id_with_email(self, real_context):
        """Test get_user_subscription_groups with external_id and email combination."""
        # Test with combination of valid external_id and email
        result = await get_user_subscription_groups(
            real_context, external_id="bb", email="test@example.com"
        )

        assert isinstance(result, SubscriptionGroupsResponse)
        assert result.message == "success"

        logger.info(
            f"External_id + email returned {result.total_count} users with subscription groups"
        )

        assert result.total_count == 1, "Should return a result for the provided identifiers"

    @pytest.mark.asyncio
    async def test_get_user_subscription_groups_external_id_with_phone(self, real_context):
        """Test get_user_subscription_groups with external_id and phone combination."""
        # Test with combination of external_id and phone (this should work)
        result = await get_user_subscription_groups(
            real_context, external_id="888", phone="5166472944"
        )

        assert isinstance(result, SubscriptionGroupsResponse)
        assert result.message == "success"

        logger.info(
            f"External_id + phone returned {result.total_count} users with subscription groups"
        )
        assert result.total_count == 1, "Should return a result for the provided identifiers"

    @pytest.mark.asyncio
    async def test_get_user_subscription_groups_validation_error_no_identifiers(self, real_context):
        """Test that validation error is raised when no identifiers are provided."""
        with pytest.raises(
            ValueError, match="At least one of external_id, email, or phone must be provided"
        ):
            await get_user_subscription_groups(real_context)

    @pytest.mark.asyncio
    async def test_get_user_subscription_groups_validation_error_email_and_phone(
        self, real_context
    ):
        """Test that validation error is raised when both email and phone are provided."""
        with pytest.raises(
            ValueError,
            match="Either an email address or a phone number should be provided, but not both",
        ):
            await get_user_subscription_groups(
                real_context, email=["test@example.com"], phone=["5166472944"]
            )


class TestSubscriptionGroupStatusRealAPI:
    """Real API validation tests for subscription group status."""

    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_get_subscription_group_status_with_external_id(self, real_context):
        """Test get_subscription_group_status with external_id."""
        # Use a known subscription group ID and external_id
        subscription_group_id = "010c0014-07e9-4060-8b0c-d830b47e249f"
        external_id = "bb"

        result = await get_subscription_group_status(
            real_context, subscription_group_id=subscription_group_id, external_id=external_id
        )

        assert isinstance(result, SubscriptionGroupStatusResponse), (
            f"Expected SubscriptionGroupStatusResponse, got {type(result)}"
        )

        assert result.message == "success", "API call should be successful"
        assert isinstance(result.status, dict), "Status should be a dictionary"

        assert external_id in result.status, f"Should have status for external_id '{external_id}'"

    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_get_subscription_group_status_with_email(self, real_context):
        """Test get_subscription_group_status with email."""
        subscription_group_id = "010c0014-07e9-4060-8b0c-d830b47e249f"
        email = "test@example.com"

        result = await get_subscription_group_status(
            real_context, subscription_group_id=subscription_group_id, email=email
        )

        assert isinstance(result, SubscriptionGroupStatusResponse), (
            f"Expected SubscriptionGroupStatusResponse, got {type(result)}"
        )
        assert email in result.status, f"Should have status for email '{email}'"

    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_get_subscription_group_status_multiple_external_ids(self, real_context):
        """Test get_subscription_group_status with multiple external_ids."""
        subscription_group_id = "010c0014-07e9-4060-8b0c-d830b47e249f"
        external_ids = ["bb", "cc"]

        result = await get_subscription_group_status(
            real_context, subscription_group_id=subscription_group_id, external_id=external_ids
        )

        assert isinstance(result, SubscriptionGroupStatusResponse)
        assert result.message == "success"
        assert isinstance(result.status, dict)

        # Should have status for all requested users
        for ext_id in external_ids:
            assert ext_id in result.status

    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_get_subscription_group_status_validation_error_no_identifiers(
        self, real_context
    ):
        """Test that validation error is raised when no identifiers are provided."""
        with pytest.raises(
            ValueError, match="At least one of external_id, email, or phone must be provided"
        ):
            await get_subscription_group_status(
                real_context, subscription_group_id="010c0014-07e9-4060-8b0c-d830b47e249f"
            )

    @pytest.mark.real_api
    @pytest.mark.asyncio
    async def test_get_subscription_group_status_validation_error_email_and_phone(
        self, real_context
    ):
        """Test that validation error is raised when both email and phone are provided without external_id."""
        with pytest.raises(
            ValueError,
            match="Either an email address or a phone number should be provided, but not both",
        ):
            await get_subscription_group_status(
                real_context,
                subscription_group_id="010c0014-07e9-4060-8b0c-d830b47e249f",
                email=["test@example.com"],
                phone=["5166472944"],
            )
