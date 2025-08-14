from pydantic import Field

from .common import BrazeBaseModel, PaginationInfo


class CatalogItem(BrazeBaseModel):
    """
    Model representing a catalog item with completely arbitrary fields.

    Each catalog can have different field structures. The only guaranteed field is 'id',
    all other fields are dynamic and depend on the catalog schema.
    """

    id: str = Field(..., description="The unique identifier for the catalog item")


class CatalogItemsResponse(BrazeBaseModel):
    """
    Model representing the response from the catalog items endpoint.
    """

    items: list[CatalogItem] = Field(..., description="List of catalog items")
    message: str = Field(..., description="Status message")


class CatalogItemsWithPagination(BrazeBaseModel):
    """
    Model representing catalog items response with pagination information.
    """

    items: list[CatalogItem] = Field(..., description="List of catalog items")
    message: str = Field(..., description="Status message")
    pagination_info: PaginationInfo = Field(..., description="Pagination information")


class CatalogSelection(BrazeBaseModel):
    """
    Model representing a selection within a catalog.
    """

    name: str = Field(..., description="The name of the selection")
    description: str | None = Field(None, description="The description of the selection")
    external_id: str | None = Field(None, description="External ID of the selection")


class CatalogField(BrazeBaseModel):
    """
    Model representing a field within a catalog.
    """

    name: str = Field(..., description="The name of the field")
    token: str = Field(..., description="The token identifier for the field")
    type: str = Field(
        ..., description="The data type of the field (string, number, boolean, time, array, object)"
    )
    is_inventory: bool | None = Field(None, description="Whether this field represents inventory")
    is_price: bool | None = Field(None, description="Whether this field represents price")


class Catalog(BrazeBaseModel):
    """
    Model representing a single catalog from the Braze API.
    """

    description: str | None = Field(None, description="The description of the catalog")
    fields: list[CatalogField] = Field(..., description="List of fields in the catalog")
    name: str = Field(..., description="The name of the catalog")
    num_items: int = Field(..., description="The number of items in the catalog")
    storage_size: int = Field(..., description="The storage size of the catalog in bytes")
    updated_at: str = Field(..., description="The timestamp when the catalog was last updated")
    source: str = Field(..., description="The source of the catalog (e.g., Braze, Shopify)")
    selections: list[CatalogSelection] = Field(..., description="List of selections in the catalog")


class CatalogsResponse(BrazeBaseModel):
    """
    Model representing the response from the get catalogs endpoint.
    """

    catalogs: list[Catalog] = Field(..., description="List of catalogs in the workspace")
    message: str = Field(..., description="Status message")
