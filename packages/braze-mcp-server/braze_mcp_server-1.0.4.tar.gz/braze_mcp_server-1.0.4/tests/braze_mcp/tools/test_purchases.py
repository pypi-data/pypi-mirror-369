from unittest.mock import patch

import pytest

from braze_mcp.models import (
    ProductListResponse,
    QuantitySeriesResponse,
    RevenueSeriesResponse,
)
from braze_mcp.tools.purchases import (
    get_product_list,
    get_quantity_series,
    get_revenue_series,
)


@pytest.fixture
def sample_product_list_data():
    return {
        "message": "success",
        "products": ["product_1", "product_2", "product_3"],
    }


@pytest.fixture
def sample_revenue_series_data():
    return {
        "message": "success",
        "data": [
            {"time": "2025-01-01", "revenue": 5000.0},
            {"time": "2025-01-02", "revenue": 6200.0},
        ],
    }


@pytest.fixture
def sample_quantity_series_data():
    return {
        "message": "success",
        "data": [
            {"time": "2025-01-01", "purchase_quantity": 150},
            {"time": "2025-01-02", "purchase_quantity": 180},
        ],
    }


class TestGetProductList:
    """Test get_product_list function"""

    @pytest.mark.asyncio
    async def test_get_product_list_success_with_default_parameters(
        self, mock_context, mock_braze_context, sample_product_list_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.purchases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.purchases.make_request",
                return_value=SuccessResponse(data=sample_product_list_data, headers={}),
            ) as mock_request:
                result = await get_product_list(mock_context)

                assert isinstance(result, ProductListResponse)
                assert result.message == "success"
                assert len(result.products) == 3
                assert "product_1" in result.products
                assert "product_2" in result.products
                assert "product_3" in result.products

                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client
                assert call_args[0][1] == mock_braze_context.base_url
                assert call_args[0][2] == "purchases/product_list"
                params = call_args[0][3]
                assert params["page"] is None

    @pytest.mark.asyncio
    async def test_get_product_list_success_with_page_parameter(
        self, mock_context, mock_braze_context, sample_product_list_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.purchases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.purchases.make_request",
                return_value=SuccessResponse(data=sample_product_list_data, headers={}),
            ) as mock_request:
                await get_product_list(mock_context, page="2")

                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["page"] == "2"

    @pytest.mark.asyncio
    async def test_get_product_list_request_failure(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.purchases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.purchases.make_request",
                return_value=FailureResponse(
                    data={"error": "Request failed"},
                    error=Exception("Request failed"),
                ),
            ):
                result = await get_product_list(mock_context)

                assert isinstance(result, dict)
                assert "error" in result
                assert result["error"] == "Request failed"

    @pytest.mark.asyncio
    async def test_get_product_list_response_fails_parsing(self, mock_context, mock_braze_context):
        """Test get product list returns the raw response when the response fails schema validation"""
        invalid_data = {"message": "success", "products": {"invalid": "format"}}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.purchases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.purchases.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ):
                with patch("braze_mcp.tools.purchases.logger.exception") as mock_logger:
                    result = await get_product_list(mock_context)

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()


class TestGetRevenueSeries:
    """Test get_revenue_series function"""

    @pytest.mark.asyncio
    async def test_get_revenue_series_success_with_required_parameters(
        self, mock_context, mock_braze_context, sample_revenue_series_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.purchases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.purchases.make_request",
                return_value=SuccessResponse(data=sample_revenue_series_data, headers={}),
            ) as mock_request:
                result = await get_revenue_series(mock_context, length=100)

                assert isinstance(result, RevenueSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 2
                assert result.data[0].time == "2025-01-01"
                assert result.data[0].revenue == 5000
                assert result.data[1].time == "2025-01-02"
                assert result.data[1].revenue == 6200

                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client
                assert call_args[0][1] == mock_braze_context.base_url
                assert call_args[0][2] == "purchases/revenue_series"
                params = call_args[0][3]
                assert params["length"] == 100
                assert params["ending_at"] is None
                assert params["unit"] is None
                assert params["app_id"] is None
                assert params["product"] is None

    @pytest.mark.asyncio
    async def test_get_revenue_series_success_with_all_parameters(
        self, mock_context, mock_braze_context, sample_revenue_series_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.purchases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.purchases.make_request",
                return_value=SuccessResponse(data=sample_revenue_series_data, headers={}),
            ) as mock_request:
                await get_revenue_series(
                    mock_context,
                    length=50,
                    ending_at="2025-01-02T23:59:59-05:00",
                    unit="day",
                    app_id="test_app_id",
                    product="test_product",
                )

                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["length"] == 50
                assert params["ending_at"] == "2025-01-02T23:59:59-05:00"
                assert params["unit"] == "day"
                assert params["app_id"] == "test_app_id"
                assert params["product"] == "test_product"

    @pytest.mark.asyncio
    async def test_get_revenue_series_request_failure(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.purchases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.purchases.make_request",
                return_value=FailureResponse(
                    data={"error": "Request failed"},
                    error=Exception("Request failed"),
                ),
            ):
                result = await get_revenue_series(mock_context, length=100)

                assert isinstance(result, dict)
                assert "error" in result


class TestGetQuantitySeries:
    """Test get_quantity_series function"""

    @pytest.mark.asyncio
    async def test_get_quantity_series_success(
        self, mock_context, mock_braze_context, sample_quantity_series_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.purchases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.purchases.make_request",
                return_value=SuccessResponse(data=sample_quantity_series_data, headers={}),
            ) as mock_request:
                result = await get_quantity_series(mock_context, length=30)

                assert isinstance(result, QuantitySeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 2
                assert result.data[0].purchase_quantity == 150
                assert result.data[1].purchase_quantity == 180

                call_args = mock_request.call_args
                assert call_args[0][2] == "purchases/quantity_series"
                params = call_args[0][3]
                assert params["length"] == 30

    @pytest.mark.asyncio
    async def test_get_quantity_series_response_fails_parsing(
        self, mock_context, mock_braze_context
    ):
        invalid_data = {"message": "success", "data": [{"invalid": "data"}]}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.purchases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.purchases.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ):
                with patch("braze_mcp.tools.purchases.logger.exception") as mock_logger:
                    result = await get_quantity_series(mock_context, length=30)

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_quantity_series_request_failure(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.purchases.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.purchases.make_request",
                return_value=FailureResponse(
                    data={"error": "Request failed"},
                    error=Exception("Request failed"),
                ),
            ):
                result = await get_quantity_series(mock_context, length=30)

                assert isinstance(result, dict)
                assert "error" in result
