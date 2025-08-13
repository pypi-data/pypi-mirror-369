from pydantic import Field

from .common import BrazeBaseModel


class CanvasDataSeriesTotalStats(BrazeBaseModel):
    """
    Model representing total statistics for a Canvas data point.
    """

    revenue: float | None = Field(None, description="The number of dollars of revenue (USD)")
    conversions: int | None = Field(None, description="The number of conversions")
    conversions_by_entry_time: int | None = Field(
        None, description="The number of conversions for the conversion event by entry time"
    )
    entries: int | None = Field(None, description="The number of entries")


class CanvasDataSeriesVariantStats(BrazeBaseModel):
    """
    Model representing variant statistics for a Canvas data point.
    """

    name: str = Field(..., description="The name of variant")
    revenue: float = Field(..., description="The number of dollars of revenue (USD)")
    conversions: int = Field(..., description="The number of conversions")
    conversions_by_entry_time: int = Field(
        ..., description="The number of conversions for the conversion event by entry time"
    )
    entries: int = Field(..., description="The number of entries")


class CanvasDataSeriesEmailMessageStats(BrazeBaseModel):
    """
    Model representing email message statistics for Canvas step data.
    """

    sent: int = Field(..., description="The number of sends")
    opens: int = Field(..., description="The number of opens")
    unique_opens: int = Field(..., description="The number of unique opens")
    clicks: int = Field(..., description="The number of clicks")


class CanvasDataSeriesSMSMessageStats(BrazeBaseModel):
    """
    Model representing SMS message statistics for Canvas step data.
    """

    sent: int = Field(..., description="The number of sends")
    sent_to_carrier: int = Field(..., description="The number of messages sent to the carrier")
    delivered: int = Field(..., description="The number of delivered messages")
    rejected: int = Field(..., description="The number of rejected messages")
    delivery_failed: int = Field(..., description="The number of failed deliveries")
    clicks: int = Field(..., description="The number of clicks on shortened links")
    opt_out: int = Field(..., description="The number of opt outs")
    help: int = Field(..., description="The number of help messages received")


class CanvasDataSeriesStepMessages(BrazeBaseModel):
    """
    Model representing message statistics by channel for Canvas step data.
    """

    email: list[CanvasDataSeriesEmailMessageStats] | None = Field(
        None, description="Email message statistics"
    )
    sms: list[CanvasDataSeriesSMSMessageStats] | None = Field(
        None, description="SMS message statistics"
    )
    # Note: Other channels can be added here following similar patterns


class CanvasDataSeriesStepStats(BrazeBaseModel):
    """
    Model representing step statistics for a Canvas data point.
    """

    name: str = Field(..., description="The name of step")
    revenue: float = Field(..., description="The number of dollars of revenue (USD)")
    conversions: int = Field(..., description="The number of conversions")
    conversions_by_entry_time: int | None = Field(
        None, description="The number of conversions for the conversion event by entry time"
    )
    messages: CanvasDataSeriesStepMessages | None = Field(
        None, description="Message statistics by channel"
    )


class CanvasDataSeriesStatsData(BrazeBaseModel):
    """
    Model representing a single Canvas data series statistics data point.
    """

    time: str = Field(..., description="The date as ISO 8601 date")
    total_stats: CanvasDataSeriesTotalStats = Field(..., description="Total statistics")
    variant_stats: dict[str, CanvasDataSeriesVariantStats] | None = Field(
        None, description="Statistics by variant (keyed by variant API identifier)"
    )
    step_stats: dict[str, CanvasDataSeriesStepStats] | None = Field(
        None, description="Statistics by step (keyed by step API identifier)"
    )


class CanvasDataSeriesData(BrazeBaseModel):
    """
    Model representing the data portion of the Canvas data series response.
    """

    name: str = Field(..., description="The Canvas name")
    stats: list[CanvasDataSeriesStatsData] = Field(
        ..., description="List of Canvas data series statistics"
    )


class CanvasDataSeriesResponse(BrazeBaseModel):
    """
    Model representing the response from the canvas/data_series endpoint.
    """

    data: CanvasDataSeriesData = Field(..., description="Canvas data series data")
    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
