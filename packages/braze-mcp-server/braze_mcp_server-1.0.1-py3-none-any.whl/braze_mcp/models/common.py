from pydantic import BaseModel, ConfigDict, Field


class BrazeBaseModel(BaseModel):
    """Base model for all Braze MCP models with extra fields allowed.

    This allows models to accept additional fields in case the Braze API
    changes response format and includes new fields not yet defined in our models.
    """

    model_config = ConfigDict(extra="allow")


class PaginationInfo(BrazeBaseModel):
    """Model representing pagination information for paginated responses."""

    current_page_count: int = Field(..., description="Number of items in the current page")
    has_more_pages: bool = Field(..., description="Whether there are more pages available")
    next_cursor: str | None = Field(None, description="Cursor for the next page, if available")
    max_per_page: int = Field(..., description="Maximum number of items per page")
    link_header: str | None = Field(None, description="Raw Link header from the API response")
