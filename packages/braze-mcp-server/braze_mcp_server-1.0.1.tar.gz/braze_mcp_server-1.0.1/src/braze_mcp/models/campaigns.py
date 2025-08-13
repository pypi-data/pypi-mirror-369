from datetime import datetime

from pydantic import Field

from .common import BrazeBaseModel


class Campaign(BrazeBaseModel):
    """
    Model representing a single campaign from the Braze campaigns/list API.
    """

    id: str = Field(..., description="The Campaign API identifier")
    last_edited: datetime = Field(
        ..., description="The last edited time for the message (ISO 8601 format)"
    )
    name: str = Field(..., description="The campaign name")
    is_api_campaign: bool = Field(..., description="Whether the campaign is an API campaign")
    tags: list[str | None] = Field(
        ...,
        description="The tag names associated with the campaign formatted as strings (may include null values)",
    )


class CampaignListResponse(BrazeBaseModel):
    """
    Model representing the response from the campaigns/list endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    campaigns: list[Campaign] = Field(..., description="List of campaigns")


class CampaignMessage(BrazeBaseModel):
    """
    Model representing a single message within a campaign.
    """

    channel: str = Field(
        ...,
        description="The channel type of the message, must be either email, ios_push, webhook, content_card, in-app_message, or sms",
    )
    name: str | None = Field(
        None,
        description="The name of the message in the dashboard (e.g., 'Variation 1'), can be null",
    )

    # Additional channel-specific fields will be included as extra fields (handled by BrazeBaseModel)


class ConversionBehavior(BrazeBaseModel):
    """
    Model representing a conversion event behavior assigned to a campaign.
    """

    type: str = Field(..., description="The name of the conversion behavior type")
    window: int = Field(
        ...,
        description="The number of seconds during which the user can convert on this event, such as 86400, which is 24 hours",
    )

    # Additional channel-specific fields will be included as extra fields (handled by BrazeBaseModel)


class CampaignDetails(BrazeBaseModel):
    """
    Model representing detailed information about a single campaign.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    created_at: datetime | None = Field(None, description="The date created as ISO 8601 date")
    updated_at: datetime | None = Field(None, description="The date last updated as ISO 8601 date")
    archived: bool | None = Field(None, description="Whether this campaign is archived")
    draft: bool | None = Field(None, description="Whether this campaign is a draft")
    enabled: bool | None = Field(None, description="Whether this campaign is active or not")
    has_post_launch_draft: bool | None = Field(
        None, description="Whether this campaign has a post-launch draft"
    )
    name: str | None = Field(None, description="The campaign name")
    description: str | None = Field(None, description="The campaign description")
    schedule_type: str | None = Field(None, description="The type of scheduling action")
    channels: list[str] | None = Field(None, description="The list of channels to send via")
    first_sent: datetime | None = Field(
        None, description="The date and hour of first sent as ISO 8601 date"
    )
    last_sent: datetime | None = Field(
        None, description="The date and hour of last sent as ISO 8601 date"
    )
    tags: list[str] | None = Field(None, description="The tag names associated with the campaign")
    teams: list[str] | None = Field(
        None, description="The names of the Teams associated with the campaign"
    )
    messages: dict[str, CampaignMessage] | None = Field(
        None,
        description="Dictionary of messages where keys are message_variation_id and values are message objects",
    )
    conversion_behaviors: list[ConversionBehavior] | None = Field(
        None, description="The conversion event behaviors assigned to the campaign"
    )
