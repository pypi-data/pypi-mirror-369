from pydantic import Field

from .common import BrazeBaseModel


class PreferenceCenter(BrazeBaseModel):
    """
    Model representing a single preference center from the Braze API.
    """

    name: str = Field(..., description="The name of the preference center")
    preference_center_api_id: str = Field(..., description="The preference center API identifier")
    created_at: str = Field(
        ..., description="The ISO 8601 timestamp when the preference center was created"
    )
    updated_at: str = Field(
        ..., description="The ISO 8601 timestamp when the preference center was last updated"
    )


class PreferenceCenterDetails(BrazeBaseModel):
    """
    Model representing detailed information for a single preference center from the Braze API.
    """

    name: str = Field(..., description="The name of the preference center")
    preference_center_api_id: str = Field(..., description="The preference center API identifier")
    created_at: str = Field(
        ..., description="The ISO 8601 timestamp when the preference center was created"
    )
    updated_at: str = Field(
        ..., description="The ISO 8601 timestamp when the preference center was last updated"
    )
    preference_center_title: str = Field(..., description="The title of the preference center")
    preference_center_page_html: str = Field(
        ..., description="The HTML content for the preference center page"
    )
    confirmation_page_html: str = Field(
        ..., description="The HTML content for the confirmation page"
    )
    redirect_page_html: str | None = Field(
        None, description="The HTML content for the redirect page, null if not set"
    )
    preference_center_options: dict[str, str] | None = Field(
        ..., description="Options for the preference center (e.g., meta-viewport-content)"
    )
    state: str = Field(
        ..., description="The current state of the preference center (active, draft)"
    )


class PreferenceCentersResponse(BrazeBaseModel):
    """
    Model representing the response from the preference_center/v1/list endpoint.
    """

    preference_centers: list[PreferenceCenter] = Field(
        ..., description="List of preference centers"
    )
