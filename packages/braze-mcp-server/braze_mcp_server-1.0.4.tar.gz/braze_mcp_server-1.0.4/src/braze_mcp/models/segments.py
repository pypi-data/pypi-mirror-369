from pydantic import Field

from .common import BrazeBaseModel


class Segment(BrazeBaseModel):
    """
    Model representing a single segment from the Braze segments/list API.
    """

    id: str = Field(..., description="The Segment API identifier")
    name: str = Field(..., description="Segment name")
    analytics_tracking_enabled: bool = Field(
        ..., description="Whether the segment has analytics tracking enabled"
    )
    tags: list[str | None] = Field(
        ...,
        description="The tag names associated with the segment formatted as strings (may include null values)",
    )


class SegmentListResponse(BrazeBaseModel):
    """
    Model representing the response from the segments/list endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    segments: list[Segment] = Field(..., description="List of segments")


class SegmentDataPoint(BrazeBaseModel):
    """
    Model representing a single data point for segment analytics.
    """

    time: str = Field(..., description="The date as ISO 8601 date")
    size: int = Field(..., description="The size of the segment on that date")


class SegmentDataSeriesResponse(BrazeBaseModel):
    """
    Model representing the response from the segments/data_series endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    data: list[SegmentDataPoint] = Field(..., description="List of segment analytics data points")


class SegmentDetails(BrazeBaseModel):
    """
    Model representing detailed information about a single segment.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    created_at: str = Field(..., description="The date created as ISO 8601 date")
    updated_at: str = Field(..., description="The date last updated as ISO 8601 date")
    name: str = Field(..., description="The segment name")
    description: str = Field(..., description="A human-readable description of filters")
    text_description: str = Field(..., description="The segment description")
    tags: list[str] = Field(
        ...,
        description="The tag names associated with the segment formatted as strings",
    )
    teams: list[str] = Field(..., description="The names of the Teams associated with the campaign")
