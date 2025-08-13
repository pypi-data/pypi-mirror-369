from pydantic import Field

from .common import BrazeBaseModel


class SessionDataPoint(BrazeBaseModel):
    """
    Model representing a single data point for session analytics.
    """

    time: str = Field(
        ...,
        description="Point in time - as ISO 8601 extended when unit is 'hour' and as ISO 8601 date when unit is 'day'",
    )
    sessions: int = Field(..., description="Number of sessions")


class SessionDataSeriesResponse(BrazeBaseModel):
    """
    Model representing the response from the sessions/data_series endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    data: list[SessionDataPoint] = Field(..., description="List of session analytics data points")
