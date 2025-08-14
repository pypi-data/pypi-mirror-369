from pydantic import Field

from .common import BrazeBaseModel


class ProductListResponse(BrazeBaseModel):
    """
    Model representing the response from the purchases/product_list endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    products: list[str] = Field(..., description="List of product names")


class RevenueDataPoint(BrazeBaseModel):
    """
    Model representing a single data point for revenue.
    """

    time: str = Field(..., description="The date as ISO 8601 date")
    revenue: float = Field(..., description="Amount of revenue for the time period")


class RevenueSeriesResponse(BrazeBaseModel):
    """
    Model representing the response from the purchases/revenue_series endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    data: list[RevenueDataPoint] = Field(..., description="List of revenue data points")


class QuantityDataPoint(BrazeBaseModel):
    """
    Model representing a single data point for purchase quantity.
    """

    time: str = Field(..., description="The date as ISO 8601 date")
    purchase_quantity: int = Field(
        ..., description="The number of items purchased in the time period"
    )


class QuantitySeriesResponse(BrazeBaseModel):
    """
    Model representing the response from the purchases/quantity_series endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    data: list[QuantityDataPoint] = Field(..., description="List of purchase quantity data points")
