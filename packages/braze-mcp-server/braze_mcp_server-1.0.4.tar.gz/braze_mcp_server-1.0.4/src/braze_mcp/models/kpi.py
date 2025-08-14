from pydantic import Field

from .common import BrazeBaseModel


class NewUsersDataPoint(BrazeBaseModel):
    """
    Model representing a single data point for new users.
    """

    time: str = Field(..., description="The date as ISO 8601 date")
    new_users: int = Field(..., description="The number of daily new users")


class NewUsersDataSeriesResponse(BrazeBaseModel):
    """
    Model representing the response from the kpi/new_users/data_series endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    data: list[NewUsersDataPoint] = Field(..., description="List of new users data points")


class DAUDataPoint(BrazeBaseModel):
    """
    Model representing a single data point for daily active users.
    """

    time: str = Field(..., description="The date as ISO 8601 date")
    dau: int = Field(..., description="The number of daily active users")


class DAUDataSeriesResponse(BrazeBaseModel):
    """
    Model representing the response from the kpi/dau/data_series endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    data: list[DAUDataPoint] = Field(..., description="List of daily active users data points")


class MAUDataPoint(BrazeBaseModel):
    """
    Model representing a single data point for monthly active users.
    """

    time: str = Field(..., description="The date as ISO 8601 date")
    mau: int = Field(..., description="The number of monthly active users")


class MAUDataSeriesResponse(BrazeBaseModel):
    """
    Model representing the response from the kpi/mau/data_series endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    data: list[MAUDataPoint] = Field(..., description="List of monthly active users data points")


class UninstallsDataPoint(BrazeBaseModel):
    """
    Model representing a single data point for app uninstalls.
    """

    time: str = Field(..., description="The date as ISO 8601 date")
    uninstalls: int = Field(..., description="The number of uninstalls")


class UninstallsDataSeriesResponse(BrazeBaseModel):
    """
    Model representing the response from the kpi/uninstalls/data_series endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    data: list[UninstallsDataPoint] = Field(..., description="List of uninstalls data points")
