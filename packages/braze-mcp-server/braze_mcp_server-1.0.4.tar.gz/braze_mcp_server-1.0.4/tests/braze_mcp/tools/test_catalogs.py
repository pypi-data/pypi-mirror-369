from unittest.mock import patch

import pytest

from braze_mcp.models import CatalogItemsResponse, CatalogItemsWithPagination, CatalogsResponse
from braze_mcp.tools.catalogs import get_catalog_item, get_catalog_items, get_catalogs


@pytest.fixture
def sample_catalogs_data():
    """Sample data for catalogs endpoint."""
    return {
        "catalogs": [
            {
                "description": "My Restaurants",
                "fields": [
                    {"name": "id", "token": "-1", "type": "string"},
                    {"name": "Name", "token": "0", "type": "string"},
                    {"name": "City", "token": "1", "type": "string"},
                    {"name": "Cuisine", "token": "2", "type": "string"},
                    {"name": "Rating", "token": "3", "type": "number"},
                    {"name": "Loyalty_Program", "token": "4", "type": "boolean"},
                    {"name": "Created_At", "token": "5", "type": "time"},
                ],
                "name": "restaurants",
                "num_items": 10,
                "storage_size": 87095,
                "updated_at": "2022-11-02T20:04:06.879+00:00",
                "source": "Braze",
                "selections": [
                    {
                        "name": "high_rated",
                        "description": "Restaurants with high ratings",
                        "external_id": "hr_001",
                    }
                ],
            },
            {
                "description": "My Catalog",
                "fields": [
                    {"name": "id", "token": "-1", "type": "string"},
                    {"name": "string_field", "token": "0", "type": "string"},
                    {"name": "number_field", "token": "1", "type": "number"},
                    {"name": "boolean_field", "token": "2", "type": "boolean"},
                    {"name": "time_field", "token": "3", "type": "time"},
                ],
                "name": "my_catalog",
                "num_items": 3,
                "storage_size": 53584,
                "updated_at": "2022-11-02T09:03:19.967+00:00",
                "source": "Braze",
                "selections": [],
            },
        ],
        "message": "success",
    }


@pytest.fixture
def empty_catalogs_data():
    """Sample data for empty catalogs response."""
    return {"catalogs": [], "message": "success"}


@pytest.fixture
def sample_catalog_items_data():
    """Sample data for catalog items endpoint with arbitrary schemas."""
    return {
        "items": [
            # Shopify catalog item example
            {
                "id": "12423297302645",
                "store_name": "yetiau",
                "shopify_product_id": "11168685844",
                "shopify_variant_id": "12423297302645",
                "product_title": "Rambler® 30 oz (887 ml) Tumbler",
                "variant_title": "Navy",
                "status": "active",
                "body_html": "<p>Iced coffee, sweet tea, lemonade, water, you name it, you're set. Fits in most cupholders.</p>",
                "product_image_url": "https://cdn.shopify.com/s/files/1/2034/2321/products/site_studio_Drinkware_Rambler_30oz_Tumbler_Charcoal_Front_4109_Primary_B_2400x2400_4adbf11f-2701-4f07-9693-532079a679da.png?v=1690427512",
                "variant_image_url": "https://cdn.shopify.com/s/files/1/2034/2321/products/Drinkware_Tumbler_30oz_Navy_Studio_PrimaryB.png?v=1690427512",
                "vendor": "YETI",
                "product_type": "Rambler",
                "published_scope": "web",
                "price": 45,
                "compare_at_price": 0,
                "inventory_quantity": 1597,
                "options": "Colour",
                "option_values": "Navy",
                "sku": "21070070027",
                "boolean": None,
                "time": None,
            },
            # Simple catalog item example
            {"id": "shirts", "stock": 3, "description": "supersale", "other": False},
            # Restaurant catalog item example
            {
                "id": "restaurant1",
                "Name": "Restaurant1",
                "City": "New York",
                "Cuisine": "American",
                "Rating": 5,
                "Loyalty_Program": True,
                "Open_Time": "2022-11-02T09:03:19.967Z",
            },
        ],
        "message": "success",
    }


@pytest.fixture
def empty_catalog_items_data():
    """Sample data for empty catalog items response."""
    return {"items": [], "message": "success"}


@pytest.fixture
def sample_catalog_item_data():
    """Sample data for single catalog item endpoint."""
    return {
        "items": [
            {
                "id": "restaurant3",
                "Name": "Restaurant1",
                "City": "New York",
                "Cuisine": "American",
                "Rating": 5,
                "Loyalty_Program": True,
                "Open_Time": "2022-11-01T09:03:19.967Z",
            }
        ],
        "message": "success",
    }


class TestGetCatalogs:
    """Test get_catalogs function"""

    @pytest.mark.asyncio
    async def test_success_response_with_catalogs(
        self, mock_context, mock_braze_context, sample_catalogs_data
    ):
        """Test successful catalogs retrieval with data."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=SuccessResponse(data=sample_catalogs_data, headers={}),
            ) as mock_request,
        ):
            result = await get_catalogs(mock_context)

            assert isinstance(result, CatalogsResponse)

            assert result.message == "success"
            assert len(result.catalogs) == 2

            first_catalog = result.catalogs[0]
            assert first_catalog.name == "restaurants"
            assert first_catalog.description == "My Restaurants"
            assert first_catalog.num_items == 10
            assert first_catalog.storage_size == 87095
            assert first_catalog.source == "Braze"
            assert first_catalog.updated_at == "2022-11-02T20:04:06.879+00:00"
            assert len(first_catalog.fields) == 7

            id_field = first_catalog.fields[0]
            assert id_field.name == "id"
            assert id_field.token == "-1"
            assert id_field.type == "string"

            rating_field = first_catalog.fields[4]
            assert rating_field.name == "Rating"
            assert rating_field.token == "3"
            assert rating_field.type == "number"

            second_catalog = result.catalogs[1]
            assert second_catalog.name == "my_catalog"
            assert second_catalog.description == "My Catalog"
            assert second_catalog.num_items == 3
            assert second_catalog.storage_size == 53584
            assert second_catalog.source == "Braze"
            assert len(second_catalog.fields) == 5
            assert len(second_catalog.selections) == 0

            # Check first catalog has selections
            assert len(first_catalog.selections) == 1
            selection = first_catalog.selections[0]
            assert selection.name == "high_rated"
            assert selection.description == "Restaurants with high ratings"
            assert selection.external_id == "hr_001"

            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[2] == "catalogs"
            assert len(args) == 3

    @pytest.mark.asyncio
    async def test_success_response_empty_catalogs(
        self, mock_context, mock_braze_context, empty_catalogs_data
    ):
        """Test successful response with no catalogs."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=SuccessResponse(data=empty_catalogs_data, headers={}),
            ),
        ):
            result = await get_catalogs(mock_context)

            assert isinstance(result, CatalogsResponse)
            assert result.message == "success"
            assert len(result.catalogs) == 0

    @pytest.mark.asyncio
    async def test_api_error_response(self, mock_context, mock_braze_context):
        """Test handling of API error response."""
        from braze_mcp.utils.http import FailureResponse

        error_data = {"error": "Invalid API key"}

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=FailureResponse(data=error_data, error=Exception("API Error")),
            ),
        ):
            result = await get_catalogs(mock_context)

            # Should return error dict when there's an API error
            assert isinstance(result, dict)
            assert result == error_data

    @pytest.mark.asyncio
    async def test_invalid_response_format(self, mock_context, mock_braze_context):
        """Test handling of invalid response format that can't be parsed by pydantic."""
        from braze_mcp.utils.http import SuccessResponse

        invalid_data = {"invalid_field": "this doesn't match the expected schema"}

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ),
        ):
            result = await get_catalogs(mock_context)

            # Should return raw dict when pydantic parsing fails
            assert isinstance(result, dict)
            assert result == invalid_data

    @pytest.mark.asyncio
    async def test_catalog_with_special_field_flags(self, mock_context, mock_braze_context):
        """Test catalog with fields that have is_inventory and is_price flags."""
        from braze_mcp.utils.http import SuccessResponse

        catalog_data = {
            "catalogs": [
                {
                    "description": "Test Catalog with Special Fields",
                    "fields": [
                        {"name": "id", "token": "-1", "type": "string"},
                        {
                            "name": "price",
                            "token": "0",
                            "type": "number",
                            "is_price": True,
                        },
                        {
                            "name": "stock",
                            "token": "1",
                            "type": "number",
                            "is_inventory": True,
                        },
                    ],
                    "name": "test_catalog",
                    "num_items": 5,
                    "storage_size": 43815,
                    "updated_at": "2023-01-01T12:00:00.000+00:00",
                    "source": "Braze",
                    "selections": [],
                }
            ],
            "message": "success",
        }

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=SuccessResponse(data=catalog_data, headers={}),
            ),
        ):
            result = await get_catalogs(mock_context)

            assert isinstance(result, CatalogsResponse)
            assert len(result.catalogs) == 1

            catalog = result.catalogs[0]
            assert catalog.name == "test_catalog"
            assert len(catalog.fields) == 3

            # Check special field flags
            price_field = catalog.fields[1]
            assert price_field.name == "price"
            assert price_field.is_price is True

            stock_field = catalog.fields[2]
            assert stock_field.name == "stock"
            assert stock_field.is_inventory is True

    @pytest.mark.asyncio
    async def test_catalog_with_null_description(self, mock_context, mock_braze_context):
        """Test catalog with null description (as seen in real API responses)."""
        from braze_mcp.utils.http import SuccessResponse

        catalog_data = {
            "catalogs": [
                {
                    "description": None,
                    "fields": [
                        {"name": "id", "token": "-1", "type": "string"},
                    ],
                    "name": "test_catalog",
                    "num_items": 0,
                    "storage_size": 69925,
                    "updated_at": "2025-04-02T22:03:05.026+00:00",
                    "source": "Braze",
                    "selections": [
                        {
                            "name": "test",
                            "description": "",
                            "external_id": None,
                        }
                    ],
                }
            ],
            "message": "success",
        }

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=SuccessResponse(data=catalog_data, headers={}),
            ),
        ):
            result = await get_catalogs(mock_context)

            assert isinstance(result, CatalogsResponse)
            assert len(result.catalogs) == 1

            catalog = result.catalogs[0]
            assert catalog.description is None
            assert len(catalog.selections) == 1
            assert catalog.selections[0].external_id is None


class TestGetCatalogItems:
    """Test get_catalog_items function"""

    @pytest.mark.asyncio
    async def test_success_response_with_items(
        self, mock_context, mock_braze_context, sample_catalog_items_data
    ):
        """Test successful catalog items retrieval with data."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=SuccessResponse(data=sample_catalog_items_data, headers={}),
            ) as mock_request,
            patch(
                "braze_mcp.tools.catalogs.extract_cursor_from_link_header",
                return_value=None,
            ),
        ):
            result = await get_catalog_items(mock_context, "restaurants")

            assert isinstance(result, CatalogItemsWithPagination)
            assert result.message == "success"
            assert len(result.items) == 3

            pagination = result.pagination_info
            assert pagination.current_page_count == 3
            assert pagination.max_per_page == 50
            assert not pagination.has_more_pages
            assert pagination.next_cursor is None

            call_args = mock_request.call_args
            assert call_args[0][0] == mock_braze_context.http_client
            assert call_args[0][1] == mock_braze_context.base_url
            assert call_args[0][2] == "catalogs/restaurants/items"
            params = call_args[0][3]
            assert params == {}

            # Check first item (Shopify catalog item)
            first_item = result.items[0]
            assert first_item.id == "12423297302645"
            assert first_item.store_name == "yetiau"  # Dynamic field access
            assert first_item.product_title == "Rambler® 30 oz (887 ml) Tumbler"
            assert first_item.price == 45
            assert first_item.inventory_quantity == 1597
            assert first_item.boolean is None

            # Check second item (Simple catalog item)
            second_item = result.items[1]
            assert second_item.id == "shirts"
            assert second_item.stock == 3
            assert second_item.description == "supersale"
            assert second_item.other is False

            # Check third item (Restaurant catalog item)
            third_item = result.items[2]
            assert third_item.id == "restaurant1"
            assert third_item.Name == "Restaurant1"
            assert third_item.Rating == 5
            assert third_item.Loyalty_Program is True

    @pytest.mark.asyncio
    async def test_success_response_with_cursor(
        self, mock_context, mock_braze_context, sample_catalog_items_data
    ):
        """Test successful catalog items retrieval with cursor parameter."""
        from braze_mcp.utils.http import SuccessResponse

        cursor = "test_cursor_123"
        sample_response_headers = {
            "content-type": "application/json",
            "link": '<https://test.braze.com/catalogs/restaurants/items?cursor=abc123>; rel="next"',
        }

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=SuccessResponse(
                    data=sample_catalog_items_data, headers=sample_response_headers
                ),
            ) as mock_request,
            patch(
                "braze_mcp.tools.catalogs.extract_cursor_from_link_header",
                return_value="abc123",
            ),
        ):
            result = await get_catalog_items(mock_context, "restaurants", cursor=cursor)

            assert isinstance(result, CatalogItemsWithPagination)
            assert result.message == "success"
            assert len(result.items) == 3

            pagination = result.pagination_info
            assert pagination.current_page_count == 3
            assert pagination.has_more_pages
            assert pagination.next_cursor == "abc123"
            assert pagination.max_per_page == 50
            assert pagination.link_header == sample_response_headers["link"]

            call_args = mock_request.call_args
            assert call_args[0][0] == mock_braze_context.http_client
            assert call_args[0][1] == mock_braze_context.base_url
            assert call_args[0][2] == "catalogs/restaurants/items"
            params = call_args[0][3]
            assert params["cursor"] == cursor

    @pytest.mark.asyncio
    async def test_success_response_empty_items(
        self, mock_context, mock_braze_context, empty_catalog_items_data
    ):
        """Test successful response with no items."""
        from braze_mcp.utils.http import SuccessResponse

        response_headers = {"content-type": "application/json"}

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=SuccessResponse(
                    data=empty_catalog_items_data, headers=response_headers
                ),
            ),
            patch(
                "braze_mcp.tools.catalogs.extract_cursor_from_link_header",
                return_value=None,
            ),
        ):
            result = await get_catalog_items(mock_context, "empty_catalog")

            assert isinstance(result, CatalogItemsWithPagination)
            assert result.message == "success"
            assert len(result.items) == 0

            pagination = result.pagination_info
            assert pagination.current_page_count == 0
            assert not pagination.has_more_pages
            assert pagination.next_cursor is None
            assert pagination.max_per_page == 50
            assert pagination.link_header is None

    @pytest.mark.asyncio
    async def test_api_error_response(self, mock_context, mock_braze_context):
        """Test handling of API error response."""
        from braze_mcp.utils.http import FailureResponse

        error_data = {
            "errors": [
                {
                    "id": "catalog-not-found",
                    "message": "Check that the catalog name is valid.",
                    "parameters": ["catalog_name"],
                    "parameter_values": ["invalid_catalog"],
                }
            ],
            "message": "Invalid Request",
        }

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=FailureResponse(data=error_data, error=Exception("API Error")),
            ),
        ):
            result = await get_catalog_items(mock_context, "invalid_catalog")

            # Should return error dict when there's an API error
            assert isinstance(result, dict)
            assert result == error_data

    @pytest.mark.asyncio
    async def test_catalog_items_parsing_error(self, mock_context, mock_braze_context):
        """Test get catalog items returns the raw response when schema validation fails"""
        invalid_data = {"message": "success", "items": [{"invalid": "data"}]}
        response_headers = {"content-type": "application/json"}
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=SuccessResponse(data=invalid_data, headers=response_headers),
            ),
            patch("braze_mcp.tools.catalogs.logger.exception") as mock_logger,
        ):
            result = await get_catalog_items(mock_context, "test_catalog")

            assert isinstance(result, dict)
            assert result == invalid_data
            mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_catalog_items_unexpected_response_type(self, mock_context, mock_braze_context):
        """Test catalog items handles unexpected response type"""
        from unittest.mock import MagicMock

        # Create a mock object that isn't SuccessResponse or FailureResponse
        unexpected_response = MagicMock()
        unexpected_response.__class__.__name__ = "UnexpectedResponse"

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=unexpected_response,
            ),
            patch("braze_mcp.tools.catalogs.logger.error") as mock_logger,
        ):
            result = await get_catalog_items(mock_context, "test_catalog")

            assert isinstance(result, dict)
            assert "error" in result
            # Check that we get a standardized error response
            assert result["success"] is False
            assert result["error"]["error_type"] == "unexpected_error"
            mock_logger.assert_called_once_with(
                f"Unexpected response type: {type(unexpected_response)}"
            )


class TestGetCatalogItem:
    """Test get_catalog_item function"""

    @pytest.mark.asyncio
    async def test_success_response_with_item(
        self, mock_context, mock_braze_context, sample_catalog_item_data
    ):
        """Test successful catalog item retrieval."""
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=SuccessResponse(data=sample_catalog_item_data, headers={}),
            ) as mock_request,
        ):
            result = await get_catalog_item(mock_context, "restaurants", "restaurant3")

            assert isinstance(result, CatalogItemsResponse)
            assert result.message == "success"
            assert len(result.items) == 1

            # Check the returned item
            item = result.items[0]
            assert item.id == "restaurant3"
            assert item.Name == "Restaurant1"
            assert item.City == "New York"
            assert item.Cuisine == "American"
            assert item.Rating == 5
            assert item.Loyalty_Program is True
            assert item.Open_Time == "2022-11-01T09:03:19.967Z"

            # Verify call was made correctly
            call_args = mock_request.call_args
            assert call_args[0][0] == mock_braze_context.http_client
            assert call_args[0][1] == mock_braze_context.base_url
            assert call_args[0][2] == "catalogs/restaurants/items/restaurant3"
            # No params expected for single item endpoint
            assert len(call_args[0]) == 3

    @pytest.mark.asyncio
    async def test_catalog_item_not_found(self, mock_context, mock_braze_context):
        """Test handling of catalog item not found (404) error."""
        from braze_mcp.utils.http import FailureResponse

        error_data = {
            "errors": [
                {
                    "id": "catalog-not-found",
                    "message": "Could not find catalog item",
                    "parameters": ["catalog_name", "item_id"],
                    "parameter_values": ["restaurants", "nonexistent"],
                }
            ],
            "message": "Not Found",
        }

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=FailureResponse(data=error_data, error=Exception("Not Found")),
            ),
        ):
            result = await get_catalog_item(mock_context, "restaurants", "nonexistent")

            # Should return error dict when there's an API error
            assert isinstance(result, dict)
            assert result == error_data

    @pytest.mark.asyncio
    async def test_catalog_item_parsing_error(self, mock_context, mock_braze_context):
        """Test get catalog item returns the raw response when schema validation fails"""
        invalid_data = {"message": "success", "items": [{"invalid": "data"}]}
        from braze_mcp.utils.http import SuccessResponse

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ),
            patch("braze_mcp.tools.catalogs.logger.exception") as mock_logger,
        ):
            result = await get_catalog_item(mock_context, "test_catalog", "test_item")

            assert isinstance(result, dict)
            assert result == invalid_data
            mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_catalog_item_unexpected_response_type(self, mock_context, mock_braze_context):
        """Test catalog item handles unexpected response type"""
        from unittest.mock import MagicMock

        # Create a mock object that isn't SuccessResponse or FailureResponse
        unexpected_response = MagicMock()
        unexpected_response.__class__.__name__ = "UnexpectedResponse"

        with (
            patch(
                "braze_mcp.tools.catalogs.get_braze_context",
                return_value=mock_braze_context,
            ),
            patch(
                "braze_mcp.tools.catalogs.make_request",
                return_value=unexpected_response,
            ),
            patch("braze_mcp.tools.catalogs.logger.error") as mock_logger,
        ):
            result = await get_catalog_item(mock_context, "test_catalog", "test_item")

            assert isinstance(result, dict)
            assert "error" in result
            # Check that we get a standardized error response
            assert result["success"] is False
            assert result["error"]["error_type"] == "unexpected_error"
            mock_logger.assert_called_once_with(
                f"Unexpected response type: {type(unexpected_response)}"
            )
