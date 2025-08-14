from unittest.mock import patch

import pytest

from braze_mcp.models import (
    DAUDataSeriesResponse,
    MAUDataSeriesResponse,
    NewUsersDataSeriesResponse,
    UninstallsDataSeriesResponse,
)
from braze_mcp.tools.kpi import (
    get_dau_data_series,
    get_mau_data_series,
    get_new_users_data_series,
    get_uninstalls_data_series,
)


@pytest.fixture
def sample_new_users_data():
    return {
        "message": "success",
        "data": [
            {"time": "2025-01-01", "new_users": 100},
            {"time": "2025-01-02", "new_users": 150},
        ],
    }


@pytest.fixture
def sample_dau_data():
    return {
        "message": "success",
        "data": [
            {"time": "2025-01-01", "dau": 1000},
            {"time": "2025-01-02", "dau": 1200},
        ],
    }


@pytest.fixture
def sample_mau_data():
    return {
        "message": "success",
        "data": [
            {"time": "2025-01-01", "mau": 5000},
            {"time": "2025-01-02", "mau": 5100},
        ],
    }


@pytest.fixture
def sample_uninstalls_data():
    return {
        "message": "success",
        "data": [
            {"time": "2025-01-01", "uninstalls": 25},
            {"time": "2025-01-02", "uninstalls": 30},
        ],
    }


class TestGetNewUsersDataSeries:
    """Test get_new_users_data_series function"""

    @pytest.mark.asyncio
    async def test_get_new_users_data_series_success_with_required_parameters(
        self, mock_context, mock_braze_context, sample_new_users_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.kpi.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.kpi.make_request",
                return_value=SuccessResponse(data=sample_new_users_data, headers={}),
            ) as mock_request:
                result = await get_new_users_data_series(mock_context, length=7)

                assert isinstance(result, NewUsersDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 2
                assert result.data[0].time == "2025-01-01"
                assert result.data[0].new_users == 100
                assert result.data[1].time == "2025-01-02"
                assert result.data[1].new_users == 150

                call_args = mock_request.call_args
                assert call_args[0][0] == mock_braze_context.http_client
                assert call_args[0][1] == mock_braze_context.base_url
                assert call_args[0][2] == "kpi/new_users/data_series"
                params = call_args[0][3]
                assert params["length"] == 7
                assert params["ending_at"] is None
                assert params["app_id"] is None

    @pytest.mark.asyncio
    async def test_get_new_users_data_series_success_with_all_parameters(
        self, mock_context, mock_braze_context, sample_new_users_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.kpi.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.kpi.make_request",
                return_value=SuccessResponse(data=sample_new_users_data, headers={}),
            ) as mock_request:
                await get_new_users_data_series(
                    mock_context,
                    length=14,
                    ending_at="2025-01-02T23:59:59-05:00",
                    app_id="test_app_id",
                )

                call_args = mock_request.call_args
                params = call_args[0][3]
                assert params["length"] == 14
                assert params["ending_at"] == "2025-01-02T23:59:59-05:00"
                assert params["app_id"] == "test_app_id"

    @pytest.mark.asyncio
    async def test_get_new_users_data_series_request_failure(
        self, mock_context, mock_braze_context
    ):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.kpi.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.kpi.make_request",
                return_value=FailureResponse(
                    data={"error": "Request failed"},
                    error=Exception("Request failed"),
                ),
            ):
                result = await get_new_users_data_series(mock_context, length=7)

                assert isinstance(result, dict)
                assert "error" in result
                assert result["error"] == "Request failed"

    @pytest.mark.asyncio
    async def test_get_new_users_data_series_response_fails_parsing(
        self, mock_context, mock_braze_context
    ):
        """Test get new users data series returns the raw response when the response fails schema validation"""
        invalid_data = {"message": "success", "data": [{"invalid": "data"}]}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.kpi.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.kpi.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ):
                with patch("braze_mcp.tools.kpi.logger.exception") as mock_logger:
                    result = await get_new_users_data_series(mock_context, length=7)

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()


class TestGetDAUDataSeries:
    """Test get_dau_data_series function"""

    @pytest.mark.asyncio
    async def test_get_dau_data_series_success(
        self, mock_context, mock_braze_context, sample_dau_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.kpi.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.kpi.make_request",
                return_value=SuccessResponse(data=sample_dau_data, headers={}),
            ) as mock_request:
                result = await get_dau_data_series(mock_context, length=10)

                assert isinstance(result, DAUDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 2
                assert result.data[0].dau == 1000
                assert result.data[1].dau == 1200

                call_args = mock_request.call_args
                assert call_args[0][2] == "kpi/dau/data_series"
                params = call_args[0][3]
                assert params["length"] == 10

    @pytest.mark.asyncio
    async def test_get_dau_data_series_request_failure(self, mock_context, mock_braze_context):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.kpi.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.kpi.make_request",
                return_value=FailureResponse(
                    data={"error": "Request failed"},
                    error=Exception("Request failed"),
                ),
            ):
                result = await get_dau_data_series(mock_context, length=10)

                assert isinstance(result, dict)
                assert "error" in result


class TestGetMAUDataSeries:
    """Test get_mau_data_series function"""

    @pytest.mark.asyncio
    async def test_get_mau_data_series_success(
        self, mock_context, mock_braze_context, sample_mau_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.kpi.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.kpi.make_request",
                return_value=SuccessResponse(data=sample_mau_data, headers={}),
            ) as mock_request:
                result = await get_mau_data_series(mock_context, length=7)

                assert isinstance(result, MAUDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 2
                assert result.data[0].mau == 5000
                assert result.data[1].mau == 5100

                call_args = mock_request.call_args
                assert call_args[0][2] == "kpi/mau/data_series"

    @pytest.mark.asyncio
    async def test_get_mau_data_series_response_fails_parsing(
        self, mock_context, mock_braze_context
    ):
        invalid_data = {"message": "success", "data": [{"invalid": "data"}]}
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.kpi.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.kpi.make_request",
                return_value=SuccessResponse(data=invalid_data, headers={}),
            ):
                with patch("braze_mcp.tools.kpi.logger.exception") as mock_logger:
                    result = await get_mau_data_series(mock_context, length=7)

                    assert isinstance(result, dict)
                    assert result == invalid_data
                    mock_logger.assert_called_once()


class TestGetUninstallsDataSeries:
    """Test get_uninstalls_data_series function"""

    @pytest.mark.asyncio
    async def test_get_uninstalls_data_series_success(
        self, mock_context, mock_braze_context, sample_uninstalls_data
    ):
        from braze_mcp.utils.http import SuccessResponse

        with patch(
            "braze_mcp.tools.kpi.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.kpi.make_request",
                return_value=SuccessResponse(data=sample_uninstalls_data, headers={}),
            ) as mock_request:
                result = await get_uninstalls_data_series(mock_context, length=14)

                assert isinstance(result, UninstallsDataSeriesResponse)
                assert result.message == "success"
                assert len(result.data) == 2
                assert result.data[0].uninstalls == 25
                assert result.data[1].uninstalls == 30

                call_args = mock_request.call_args
                assert call_args[0][2] == "kpi/uninstalls/data_series"

    @pytest.mark.asyncio
    async def test_get_uninstalls_data_series_request_failure(
        self, mock_context, mock_braze_context
    ):
        from braze_mcp.utils.http import FailureResponse

        with patch(
            "braze_mcp.tools.kpi.get_braze_context",
            return_value=mock_braze_context,
        ):
            with patch(
                "braze_mcp.tools.kpi.make_request",
                return_value=FailureResponse(
                    data={"error": "Request failed"},
                    error=Exception("Request failed"),
                ),
            ):
                result = await get_uninstalls_data_series(mock_context, length=14)

                assert isinstance(result, dict)
                assert "error" in result
