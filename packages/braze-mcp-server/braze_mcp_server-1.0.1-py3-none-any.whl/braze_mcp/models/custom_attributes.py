from pydantic import Field

from .common import BrazeBaseModel, PaginationInfo


class CustomAttribute(BrazeBaseModel):
    """
    Model representing a single custom attribute from the Braze API.
    """

    array_length: int | None = Field(
        None, description="The maximum array length, or null if not applicable"
    )
    data_type: str = Field(..., description="The data type of the attribute")
    description: str | None = Field(None, description="The attribute description")
    name: str = Field(..., description="The attribute name")
    status: str = Field(..., description="The attribute status (e.g., 'Active')")
    tag_names: list[str] = Field(..., description="The tag names associated with the attribute")


class CustomAttributesResponse(BrazeBaseModel):
    """
    Model representing the response from the custom attributes export endpoint.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    attributes: list[CustomAttribute] = Field(..., description="List of custom attributes")


class CustomAttributesWithPagination(BrazeBaseModel):
    """
    Model representing custom attributes response with pagination information.
    """

    message: str = Field(
        ...,
        description="The status of the export, returns 'success' when completed without errors",
    )
    attributes: list[CustomAttribute] = Field(..., description="List of custom attributes")
    pagination_info: PaginationInfo = Field(
        ..., description="Pagination information for navigating through results"
    )
