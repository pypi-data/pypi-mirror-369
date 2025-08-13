from pydantic import Field

from .common import BrazeBaseModel
from .message_statistics import MessageStatistics


class CampaignDataSeriesData(BrazeBaseModel):
    """
    Model representing a single campaign DataSeries data point.
    """

    time: str = Field(..., description="The date as ISO 8601 date")
    conversions_by_send_time: int | None = Field(None, description="Conversions by send time")
    conversions1_by_send_time: int | None = Field(None, description="Conversions1 by send time")
    conversions2_by_send_time: int | None = Field(None, description="Conversions2 by send time")
    conversions3_by_send_time: int | None = Field(None, description="Conversions3 by send time")
    conversions: int | None = Field(None, description="Total conversions")
    conversions1: int | None = Field(None, description="Conversions1")
    conversions2: int | None = Field(None, description="Conversions2")
    conversions3: int | None = Field(None, description="Conversions3")
    unique_recipients: int = Field(..., description="Number of unique recipients")
    revenue: float | None = Field(None, description="Revenue generated")
    messages: MessageStatistics = Field(..., description="Message statistics by channel")


class CampaignDataSeriesResponse(BrazeBaseModel):
    """
    Model representing the response from the campaign DataSeries endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    data: list[CampaignDataSeriesData] = Field(
        ..., description="List of campaign DataSeries data points"
    )
