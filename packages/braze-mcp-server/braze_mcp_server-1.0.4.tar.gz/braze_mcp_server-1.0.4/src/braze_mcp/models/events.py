from pydantic import Field

from .common import BrazeBaseModel, PaginationInfo


class EventListResponse(BrazeBaseModel):
    """
    Model representing the response from the events/list endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    events: list[str] = Field(
        ...,
        description="List of custom event names returned in groups of 250, sorted alphabetically",
    )


class EventDataSeriesDataPoint(BrazeBaseModel):
    """
    Model representing a single data point in the events data series.
    """

    time: str = Field(
        ...,
        description="The point in time - as ISO 8601 extended when unit is 'hour' and as ISO 8601 date when unit is 'day'",
    )
    count: int = Field(..., description="The number of occurrences of provided custom event")


class EventDataSeriesResponse(BrazeBaseModel):
    """
    Model representing the response from the events/data_series endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    data: list[EventDataSeriesDataPoint] = Field(
        ..., description="Series of the number of occurrences of the custom event over time"
    )


class Event(BrazeBaseModel):
    """
    Model representing a single custom event from the events endpoint.
    """

    name: str = Field(..., description="The event name")
    description: str | None = Field(None, description="The event description")
    included_in_analytics_report: bool = Field(..., description="The analytics report inclusion")
    status: str = Field(..., description="The event status")
    tag_names: list[str | None] = Field(
        ...,
        description="The tag names associated with the event formatted as strings (may include null values)",
    )


class EventsResponse(BrazeBaseModel):
    """
    Model representing the response from the events endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    events: list[Event] = Field(
        ..., description="List of custom events returned in groups of 50, sorted alphabetically"
    )


class EventsWithPagination(BrazeBaseModel):
    """
    Model representing events response with pagination information.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    events: list[Event] = Field(
        ..., description="List of custom events returned in groups of 50, sorted alphabetically"
    )
    pagination_info: PaginationInfo = Field(
        ..., description="Pagination information for navigating through results"
    )
