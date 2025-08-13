from pydantic import Field

from .common import BrazeBaseModel


class SubscriptionGroup(BrazeBaseModel):
    """
    Model representing a single subscription group from the Braze API.
    """

    channel: str = Field(
        ..., description="The channel for the subscription group (email, sms, etc.)"
    )
    id: str = Field(..., description="The subscription group identifier")
    name: str = Field(..., description="The name of the subscription group")
    status: str = Field(..., description="The subscription status (Subscribed, Unsubscribed)")


class UserSubscriptionGroups(BrazeBaseModel):
    """
    Model representing a user and their subscription groups.
    """

    email: str | None = Field(None, description="The user's email address")
    external_id: str | None = Field(None, description="The user's external ID")
    phone: str | None = Field(None, description="The user's phone number")
    subscription_groups: list[SubscriptionGroup] = Field(
        ..., description="List of subscription groups for this user"
    )


class SubscriptionGroupsResponse(BrazeBaseModel):
    """
    Model representing the response from the subscription/user/status endpoint.
    """

    message: str = Field(..., description="The response message")
    total_count: int = Field(..., description="Total number of users returned")
    users: list[UserSubscriptionGroups] = Field(
        ..., description="List of users and their subscription groups"
    )


class SubscriptionGroupStatusResponse(BrazeBaseModel):
    """
    Model representing the response from the subscription/status/get endpoint.
    """

    message: str = Field(..., description="The response message")
    status: dict[str, str] = Field(
        ...,
        description="Dictionary mapping user identifiers to subscription status (Subscribed, Unsubscribed, Unknown)",
    )
