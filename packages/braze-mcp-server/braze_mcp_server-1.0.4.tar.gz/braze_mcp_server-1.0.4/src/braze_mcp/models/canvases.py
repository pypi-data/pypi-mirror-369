from datetime import datetime

from pydantic import Field

from .common import BrazeBaseModel


class Canvas(BrazeBaseModel):
    """
    Model representing a single canvas from the Braze canvas/list API.
    """

    id: str = Field(..., description="The Canvas API identifier")
    last_edited: datetime = Field(
        ..., description="The last edited time for the canvas (ISO 8601 format)"
    )
    name: str = Field(..., description="The Canvas name")
    tags: list[str | None] = Field(
        ...,
        description="The tag names associated with the Canvas formatted as strings (may include null values)",
    )


class CanvasListResponse(BrazeBaseModel):
    """
    Model representing the response from the canvas/list endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    canvases: list[Canvas] = Field(..., description="List of canvases")


class CanvasVariant(BrazeBaseModel):
    """
    Model representing a canvas variant.
    """

    name: str = Field(..., description="The name of variant")
    id: str = Field(..., description="The API identifier of the variant")
    first_step_ids: list[str] = Field(
        ..., description="The API identifiers for first steps in variant"
    )
    first_step_id: str | None = Field(
        None,
        description="The API identifier of first step in variant (deprecated in November 2017, only included if the variant has only one first step)",
    )


class CanvasStepNextPath(BrazeBaseModel):
    """
    Model representing a next path in a canvas step.
    """

    name: str | None = Field(
        None,
        description="The name of the path - for Decision Splits this should be 'Yes' or 'No', for Audience/Action Paths this should be the group name, for Experiment Paths this should be the path name, for other steps this should be null",
    )
    next_step_id: str = Field(
        ..., description="IDs for next steps that are full steps or Message steps"
    )


class CanvasStepMessage(BrazeBaseModel):
    """
    Model representing a message within a canvas step.
    """

    channel: str = Field(
        ...,
        description="The channel type of the message (for example, 'email', 'push', 'sms', 'in_app_message')",
    )

    # Additional channel-specific fields will be included as extra fields (handled by BrazeBaseModel)


class CanvasStep(BrazeBaseModel):
    """
    Model representing a canvas step.
    """

    name: str = Field(..., description="The name of step")
    type: str = Field(..., description="The type of Canvas component")
    id: str = Field(..., description="The API identifier of the step")
    next_step_ids: list[str] = Field(
        ...,
        description="IDs for next steps that are full steps or Message steps",
    )
    next_paths: list[CanvasStepNextPath] = Field(
        ..., description="Array of next paths with names and step IDs"
    )
    channels: list[str] = Field(..., description="The channels used in step")
    messages: dict[str, CanvasStepMessage] = Field(
        ...,
        description="Dictionary of messages where keys are message_variation_id and values are message objects",
    )


class CanvasDetails(BrazeBaseModel):
    """
    Model representing detailed information about a single canvas.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    created_at: str | None = Field(None, description="The date created as ISO 8601 date")
    updated_at: str | None = Field(None, description="The date updated as ISO 8601 date")
    name: str | None = Field(None, description="The Canvas name")
    description: str | None = Field(None, description="The Canvas description")
    archived: bool | None = Field(None, description="Whether this Canvas is archived")
    draft: bool | None = Field(None, description="Whether this Canvas is a draft")
    enabled: bool | None = Field(None, description="Whether this Canvas is active or not")
    has_post_launch_draft: bool | None = Field(
        None, description="Whether this Canvas has a post-launch draft"
    )
    schedule_type: str | None = Field(None, description="The type of scheduling action")
    first_entry: str | None = Field(None, description="The date of first entry as ISO 8601 date")
    last_entry: str | None = Field(None, description="The date of last entry as ISO 8601 date")
    channels: list[str] | None = Field(None, description="Step channels used with Canvas")
    variants: list[CanvasVariant] | None = Field(None, description="List of canvas variants")
    tags: list[str] | None = Field(None, description="The tag names associated with the Canvas")
    teams: list[str] | None = Field(
        None, description="The names of the Teams associated with the Canvas"
    )
    steps: list[CanvasStep] | None = Field(None, description="List of canvas steps")


class CanvasDataSummaryTotalStats(BrazeBaseModel):
    """
    Model representing total statistics in canvas data summary.
    """

    revenue: float | None = Field(None, description="The number of dollars of revenue (USD)")
    conversions: int | None = Field(None, description="The number of conversions")
    conversions_by_entry_time: int | None = Field(
        None,
        description="The number of conversions for the conversion event by entry time",
    )
    entries: int | None = Field(None, description="The number of entries")


class CanvasDataSummaryVariantStats(BrazeBaseModel):
    """
    Model representing variant statistics in canvas data summary.
    """

    name: str | None = Field(None, description="The name of variant")
    revenue: float | None = Field(None, description="The number of dollars of revenue (USD)")
    conversions: int | None = Field(None, description="The number of conversions")
    entries: int | None = Field(None, description="The number of entries")


class CanvasDataSummaryChannelStats(BrazeBaseModel):
    """
    Model representing channel statistics within step messages.
    """

    sent: int | None = Field(None, description="The number of sends")
    opens: int | None = Field(None, description="The number of opens")
    influenced_opens: int | None = Field(None, description="The number of influenced opens")
    bounces: int | None = Field(None, description="The number of bounces")

    # Additional channel-specific fields will be included as extra fields (handled by BrazeBaseModel)


class CanvasDataSummaryStepStats(BrazeBaseModel):
    """
    Model representing step statistics in canvas data summary.
    """

    name: str | None = Field(None, description="The name of step")
    revenue: float | None = Field(None, description="The number of dollars of revenue (USD)")
    conversions: int | None = Field(None, description="The number of conversions")
    conversions_by_entry_time: int | None = Field(
        None,
        description="The number of conversions for the conversion event by entry time",
    )
    messages: dict[str, list[CanvasDataSummaryChannelStats]] | None = Field(
        None,
        description="Dictionary of messages where keys are channel names and values are lists of channel statistics",
    )


class CanvasDataSummaryData(BrazeBaseModel):
    """
    Model representing the data section of canvas data summary response.
    """

    name: str | None = Field(None, description="The Canvas name")
    total_stats: CanvasDataSummaryTotalStats | None = Field(
        None, description="Total statistics for the canvas"
    )
    variant_stats: dict[str, CanvasDataSummaryVariantStats] | None = Field(
        None,
        description="Dictionary of variant statistics where keys are variant API identifiers",
    )
    step_stats: dict[str, CanvasDataSummaryStepStats] | None = Field(
        None,
        description="Dictionary of step statistics where keys are step API identifiers",
    )


class CanvasDataSummaryResponse(BrazeBaseModel):
    """
    Model representing the response from the canvas/data_summary endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    data: CanvasDataSummaryData | None = Field(None, description="The canvas data summary")
