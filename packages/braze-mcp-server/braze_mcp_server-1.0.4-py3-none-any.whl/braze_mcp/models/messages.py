from pydantic import Field

from .common import BrazeBaseModel


class ScheduledBroadcast(BrazeBaseModel):
    """Model representing a single scheduled broadcast (campaign or canvas)."""

    name: str = Field(..., description="The name of the scheduled broadcast")
    id: str = Field(..., description="The Canvas or campaign identifier")
    type: str = Field(..., description="The broadcast type either Canvas or Campaign")
    tags: list[str] = Field(..., description="An array of tag names formatted as strings")
    next_send_time: str = Field(
        ...,
        description="The next send time formatted in ISO 8601, may also include time zone if not local/intelligent delivery",
    )
    schedule_type: str = Field(
        ...,
        description="The schedule type, either local_time_zones, intelligent_delivery or the name of your company's time zone",
    )


class ScheduledBroadcastsResponse(BrazeBaseModel):
    """Model representing the response from the messages/scheduled_broadcasts endpoint."""

    scheduled_broadcasts: list[ScheduledBroadcast] = Field(
        ..., description="List of scheduled campaigns and canvases"
    )
