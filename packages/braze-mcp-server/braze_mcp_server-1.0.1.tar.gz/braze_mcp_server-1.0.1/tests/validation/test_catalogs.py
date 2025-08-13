"""Real API validation tests for catalogs tools."""

import pytest

from braze_mcp.models.catalogs import (
    CatalogItemsResponse,
    CatalogItemsWithPagination,
    CatalogsResponse,
)
from braze_mcp.tools.catalogs import get_catalog_item, get_catalog_items, get_catalogs
from braze_mcp.utils import get_logger

logger = get_logger(__name__)


@pytest.mark.real_api
class TestCatalogsRealAPI:
    """Real API tests for catalogs tools."""

    @pytest.mark.asyncio
    async def test_get_catalogs_success(self, real_context):
        """Test get_catalogs with real API call."""
        result = await get_catalogs(real_context)

        assert isinstance(result, CatalogsResponse), (
            f"Expected CatalogsResponse, got {type(result)}"
        )

        assert result.message == "success", "API call should be successful"

        logger.info(f"Found {len(result.catalogs)} catalogs in workspace")

    @pytest.mark.asyncio
    async def test_get_catalog_items_success(self, real_context):
        """Test get_catalog_items with real API call."""
        # First, get list of catalogs to find one to test with
        catalogs_result = await get_catalogs(real_context)

        assert isinstance(catalogs_result, CatalogsResponse)

        if len(catalogs_result.catalogs) == 0:
            logger.info("No catalogs found - skipping catalog items test")
            pytest.skip("No catalogs available for testing catalog items")

        # Use the first catalog for testing
        test_catalog = catalogs_result.catalogs[0]
        logger.info(f"Testing catalog items for catalog: {test_catalog.name}")

        result = await get_catalog_items(real_context, test_catalog.name)

        assert isinstance(result, CatalogItemsWithPagination), (
            f"Expected CatalogItemsWithPagination, got {type(result)}"
        )

        assert result.message == "success", "API call should be successful"

        logger.info(f"Found {len(result.items)} items in catalog '{test_catalog.name}'")

        # Validate pagination info
        assert result.pagination_info is not None, "Pagination info should be present"
        assert result.pagination_info.current_page_count == len(result.items), (
            "Current page count should match items length"
        )
        assert result.pagination_info.max_per_page == 50, "Max per page should be 50"

        if result.pagination_info.has_more_pages:
            logger.info(
                f"Catalog has more pages, next cursor: {result.pagination_info.next_cursor}"
            )
        else:
            logger.info("Catalog has no more pages")

    @pytest.mark.asyncio
    async def test_get_catalog_items_nonexistent_catalog(self, real_context):
        """Test catalog items with nonexistent catalog name."""
        result = await get_catalog_items(real_context, "nonexistent_catalog_12345")

        # Should return error dict for nonexistent catalog
        assert isinstance(result, dict), "Expected error dict for nonexistent catalog"

        # Check for error structure
        assert result["error"]["details"] == "HTTP 404"

        logger.info("Correctly handled nonexistent catalog request")

    @pytest.mark.asyncio
    async def test_get_catalog_item_success(self, real_context):
        """Test get_catalog_item with real API call - full integration workflow."""
        # Use known catalog for testing
        test_catalog = "nr-yeti-test"
        logger.info(f"Testing catalog item for catalog: {test_catalog}")

        # Use known item for testing
        test_item = "12423297302645"
        logger.info(f"Testing catalog item with ID: {test_item}")

        result = await get_catalog_item(real_context, test_catalog, test_item)

        assert isinstance(result, CatalogItemsResponse), (
            f"Expected CatalogItemsResponse, got {type(result)}"
        )

        assert result.message == "success", "API call should be successful"
        assert len(result.items) == 1, "Should return exactly one item"

        # Verify the returned item
        item = result.items[0]
        assert item.id == test_item, "Returned item ID should match requested ID"
        logger.info(
            f"Successfully retrieved catalog item '{item.id}' from catalog '{test_catalog}'"
        )

        # Log available fields for debugging
        item_dict = item.model_dump()
        logger.info(f"Item has {len(item_dict)} fields: {list(item_dict.keys())}")

    @pytest.mark.asyncio
    async def test_get_catalog_item_nonexistent_catalog(self, real_context):
        """Test get_catalog_item with non-existent item ID."""
        # Use known catalog for testing
        test_catalog = "bogus"
        logger.info(f"Testing catalog item for catalog: {test_catalog}")

        nonexistent_item_id = "nonexistent_item_12345"
        result = await get_catalog_item(real_context, test_catalog, nonexistent_item_id)

        # Should return error dict for unknown catalog
        assert isinstance(result, dict), "Expected error dict for unknown catalog"

        assert result["error"]["details"] == "HTTP 404", (
            "Should return 404 error for non-existent item"
        )

        logger.info(
            f"Correctly handled non-existent item request for missing catalog'{test_catalog}'"
        )

    @pytest.mark.asyncio
    async def test_get_catalog_item_not_found(self, real_context):
        """Test get_catalog_item with non-existent item ID."""
        # Use known catalog for testing
        test_catalog = "nr-yeti-test"
        logger.info(f"Testing catalog item for catalog: {test_catalog}")

        nonexistent_item_id = "nonexistent_item_12345"
        result = await get_catalog_item(real_context, test_catalog, nonexistent_item_id)

        # Should return error dict for non-existent item
        assert isinstance(result, dict), "Expected error dict for non-existent item"

        # Check for error structure (similar to nonexistent catalog test)
        assert result["error"]["details"] == "HTTP 404", (
            "Should return 404 error for non-existent item"
        )

        logger.info(f"Correctly handled non-existent item request for ID '{nonexistent_item_id}'")
