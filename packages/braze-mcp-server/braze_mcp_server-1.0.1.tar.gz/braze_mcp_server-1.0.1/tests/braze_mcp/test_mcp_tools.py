from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from braze_mcp.server import call_function, list_functions
from braze_mcp.utils.context import BrazeContext


class TestListFunctions:
    """Test the list_functions tool"""

    @pytest.mark.asyncio
    async def test_list_functions_returns_registry(self):
        """Test that list_functions returns the function registry"""
        result = await list_functions()

        assert "available_functions" in result
        assert "total_functions" in result
        assert isinstance(result["available_functions"], dict)
        assert isinstance(result["total_functions"], int)

        # Check that all expected functions are in the registry
        functions = result["available_functions"]
        expected_functions = {
            # Campaigns
            "get_campaign_list",
            "get_campaign_details",
            "get_campaign_dataseries",
            # Canvases
            "get_canvas_list",
            "get_canvas_details",
            "get_canvas_data_summary",
            "get_canvas_data_series",
            # Catalogs
            "get_catalog_item",
            "get_catalog_items",
            "get_catalogs",
            # Custom Attributes
            "get_custom_attributes",
            # Events
            "get_events_list",
            "get_events_data_series",
            "get_events",
            # Integrations
            "list_integrations",
            "get_integration_job_sync_status",
            # KPI
            "get_new_users_data_series",
            "get_dau_data_series",
            "get_mau_data_series",
            "get_uninstalls_data_series",
            # Messages
            "get_scheduled_broadcasts",
            # Preference Centers
            "get_preference_centers",
            "get_preference_center_details",
            # Purchases
            "get_product_list",
            "get_revenue_series",
            "get_quantity_series",
            # SDK Authentication
            "get_sdk_authentication_keys",
            # Segments
            "get_segment_list",
            "get_segment_data_series",
            "get_segment_details",
            # Sends
            "get_send_data_series",
            # Sessions
            "get_session_data_series",
            # Subscription Groups
            "get_user_subscription_groups",
            "get_subscription_group_status",
            # Templates
            "get_content_blocks",
            "get_content_block_info",
            "get_email_templates",
            "get_email_template_info",
        }

        discovered_functions = set(functions.keys())
        assert expected_functions == discovered_functions, (
            f"Function availability mismatch.\n"
            f"Missing: {expected_functions - discovered_functions}\n"
            f"Extra: {discovered_functions - expected_functions}"
        )

        # Verify function metadata structure
        for func_name, func_info in functions.items():
            assert "description" in func_info
            assert "parameters" in func_info
            assert isinstance(func_info["description"], str)
            assert isinstance(func_info["parameters"], dict)

            # Verify return information is included (should be present for all functions)
            assert "returns" in func_info, f"Function {func_name} missing return information"
            assert "description" in func_info["returns"], (
                f"Function {func_name} missing return description"
            )
            assert "type" in func_info["returns"], f"Function {func_name} missing return type"
            assert isinstance(func_info["returns"]["description"], str)
            assert isinstance(func_info["returns"]["type"], str)


class TestCallFunction:
    """Test the call_function MCP server mechanism"""

    @pytest.fixture
    def mock_context(self):
        mock_ctx = MagicMock()
        mock_ctx.request_context = MagicMock()
        mock_ctx.request_context.lifespan_context = BrazeContext(
            api_key="test_api_key",
            base_url="https://test.braze.com",
            http_client=AsyncMock(),
        )
        return mock_ctx

    @pytest.mark.asyncio
    async def test_call_function_invalid_function_name(self, mock_context):
        """Test call_function with invalid function name"""
        result = await call_function(mock_context, "nonexistent_function")

        assert "error" in result
        assert result["success"] is False
        assert result["error"]["error_type"] == "function_not_found"
        assert "nonexistent_function" in result["error"]["message"]
        assert "not found" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_call_function_dict_parameters(self, mock_context):
        """Test call_function with dictionary parameters"""
        mock_data = {"campaigns": [], "message": "success"}

        with patch("braze_mcp.tools.campaigns.make_request") as mock_make_request:
            from braze_mcp.utils.http import SuccessResponse

            mock_make_request.return_value = SuccessResponse(data=mock_data, headers={})

            # Pass parameters as dictionary
            params = {"page": 1, "include_archived": True}
            result = await call_function(mock_context, "get_campaign_list", params)

            # call_function should return data with schema when Pydantic models are returned
            assert "data" in result
            assert "schema" in result
            assert "campaigns" in result["data"]

    @pytest.mark.asyncio
    async def test_call_function_json_string_parameters(self, mock_context):
        """Test call_function with valid JSON string parameters"""
        mock_data = {"campaigns": [], "message": "success"}

        with patch("braze_mcp.tools.campaigns.make_request") as mock_make_request:
            from braze_mcp.utils.http import SuccessResponse

            mock_make_request.return_value = SuccessResponse(data=mock_data, headers={})

            # Pass parameters as JSON string
            params = '{"page": 1, "include_archived": true}'
            result = await call_function(mock_context, "get_campaign_list", params)

            # Should successfully parse and work
            assert "data" in result
            assert "campaigns" in result["data"]

    @pytest.mark.asyncio
    async def test_call_function_invalid_json_string(self, mock_context):
        """Test call_function with invalid JSON string parameters"""
        # Pass invalid JSON string
        params = '{"page": 1, "invalid": }'  # Missing value after colon
        result = await call_function(mock_context, "get_campaign_list", params)

        assert "error" in result
        assert result["success"] is False
        assert result["error"]["error_type"] == "invalid_parameters"
        assert "Invalid JSON in parameters string" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_call_function_json_string_not_dict(self, mock_context):
        """Test call_function with JSON string that doesn't parse to dictionary"""
        # Pass JSON string that parses to a list, not a dict
        params = '["item1", "item2"]'
        result = await call_function(mock_context, "get_campaign_list", params)

        assert "error" in result
        assert result["success"] is False
        assert result["error"]["error_type"] == "invalid_parameters"
        assert (
            "Parameters string must parse to a JSON object/dictionary" in result["error"]["message"]
        )

    @pytest.mark.asyncio
    async def test_call_function_json_string_primitive_type(self, mock_context):
        """Test call_function with JSON string that parses to primitive type"""
        # Pass JSON string that parses to a string
        params = '"simple_string"'
        result = await call_function(mock_context, "get_campaign_list", params)

        assert "error" in result
        assert result["success"] is False
        assert result["error"]["error_type"] == "invalid_parameters"
        assert (
            "Parameters string must parse to a JSON object/dictionary" in result["error"]["message"]
        )

    @pytest.mark.asyncio
    async def test_call_function_empty_json_object(self, mock_context):
        """Test call_function with empty JSON object as string"""
        mock_data = {"campaigns": [], "message": "success"}

        with patch("braze_mcp.tools.campaigns.make_request") as mock_make_request:
            from braze_mcp.utils.http import SuccessResponse

            mock_make_request.return_value = SuccessResponse(data=mock_data, headers={})

            # Pass empty JSON object as string
            params = "{}"
            result = await call_function(mock_context, "get_campaign_list", params)

            # Should successfully parse empty dict and work
            assert "data" in result
            assert "campaigns" in result["data"]

    @pytest.mark.asyncio
    async def test_call_function_none_parameters(self, mock_context):
        """Test call_function with None parameters (existing behavior)"""
        mock_data = {"campaigns": [], "message": "success"}

        with patch("braze_mcp.tools.campaigns.make_request") as mock_make_request:
            from braze_mcp.utils.http import SuccessResponse

            mock_make_request.return_value = SuccessResponse(data=mock_data, headers={})

            # Pass None parameters
            result = await call_function(mock_context, "get_campaign_list", None)

            # Should work with None (existing behavior)
            assert "data" in result
            assert "campaigns" in result["data"]

    @pytest.mark.asyncio
    async def test_call_function_exception_handling(self, mock_context):
        """Test that exceptions in function calls are properly handled"""
        with patch("braze_mcp.tools.campaigns.make_request") as mock_make_request:
            mock_make_request.side_effect = Exception("Test exception")

            result = await call_function(mock_context, "get_campaign_list")

            assert "error" in result
            assert result["success"] is False
            assert result["error"]["error_type"] == "internal_error"
            assert "Error calling function" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_call_function_basic_integration(self, mock_context):
        """Test basic integration - that call_function can successfully route to each function type"""
        mock_campaign_data = {"campaigns": [], "message": "success"}
        mock_attributes_data = {"attributes": [], "message": "success"}
        mock_details_data = {"message": "success", "name": "Test Campaign"}

        # Test campaign list
        with patch("braze_mcp.tools.campaigns.make_request") as mock_make_request:
            from braze_mcp.utils.http import SuccessResponse

            mock_make_request.return_value = SuccessResponse(data=mock_campaign_data, headers={})

            result = await call_function(mock_context, "get_campaign_list")
            # Tools return structured data with schema when Pydantic models are returned
            assert "data" in result
            assert "campaigns" in result["data"]

        # Test custom attributes
        with patch("braze_mcp.tools.custom_attributes.make_request") as mock_make_request:
            mock_make_request.return_value = SuccessResponse(data=mock_attributes_data, headers={})

            result = await call_function(mock_context, "get_custom_attributes")
            assert "data" in result
            assert "schema" in result
            assert "attributes" in result["data"]

        # Test campaign details
        with patch("braze_mcp.tools.campaigns.make_request") as mock_make_request:
            mock_make_request.return_value = SuccessResponse(data=mock_details_data, headers={})

            result = await call_function(
                mock_context, "get_campaign_details", {"campaign_id": "test_id"}
            )
            # Tools return structured data with schema when Pydantic models are returned
            assert "data" in result
            assert "message" in result["data"]

    @pytest.mark.asyncio
    async def test_pydantic_responses_include_schema_information(self, mock_context):
        """
        When MCP functions return Pydantic models, the response should include:
        1. The actual data in a 'data' field
        2. Complete schema information in a 'schema' field

        This test verifies that complex models with nested objects are properly documented.
        """
        # Arrange: Create realistic campaign data with nested structures
        campaign_data = {
            "message": "success",
            "name": "Holiday Email Campaign",
            "description": "Black Friday promotional campaign",
            "enabled": True,
            "draft": False,
            "channels": ["email", "push"],
            "messages": {"email_variant": {"channel": "email", "name": "Black Friday Email"}},
            "conversion_behaviors": [{"type": "click", "window": 86400}],
        }

        # Mock the API response
        with patch("braze_mcp.tools.campaigns.make_request") as mock_request:
            from braze_mcp.utils.http import SuccessResponse

            mock_request.return_value = SuccessResponse(data=campaign_data, headers={})

            # Act: Call the function
            response = await call_function(
                mock_context, "get_campaign_details", {"campaign_id": "test123"}
            )

            # Assert: Response has the expected two-part structure
            assert set(response.keys()) == {"data", "schema"}, (
                "Response should have exactly 'data' and 'schema' fields"
            )

            # Assert: Data contains our campaign information
            self._assert_data_matches_input(response["data"], campaign_data)

            # Assert: Schema provides complete type information
            self._assert_schema_is_complete(response["schema"])

    def _assert_data_matches_input(self, actual_data, expected_data):
        """Verify that all input fields are preserved in the response data"""
        for field, expected_value in expected_data.items():
            assert actual_data[field] == expected_value, (
                f"Field '{field}' should contain the original value"
            )

    def _assert_schema_is_complete(self, schema):
        """Verify that schema contains complete type and structure information"""
        # Schema metadata should identify the model
        assert schema["model_name"] == "CampaignDetails"
        assert "CampaignDetails model" in schema["description"]

        # Schema should contain JSON Schema specification
        json_schema = schema["fields"]
        assert json_schema["type"] == "object"

        # All data fields should have type definitions
        properties = json_schema["properties"]
        required_fields = [
            "message",
            "name",
            "description",
            "enabled",
            "draft",
            "channels",
            "messages",
            "conversion_behaviors",
        ]

        for field in required_fields:
            assert field in properties, f"Schema missing field definition: {field}"
            field_schema = properties[field]

            # Each field should have type information (direct type, union, or reference)
            has_type_info = any(
                key in field_schema for key in ["type", "anyOf", "$ref"]
            ) or "$ref" in str(field_schema)
            assert has_type_info, f"Field '{field}' lacks type information"

        # Nested models should be fully defined
        nested_definitions = json_schema["$defs"]
        expected_models = ["CampaignMessage", "ConversionBehavior"]

        for model_name in expected_models:
            assert model_name in nested_definitions, (
                f"Missing definition for nested model: {model_name}"
            )

            model_def = nested_definitions[model_name]
            assert model_def["type"] == "object"
            assert "properties" in model_def
            assert len(model_def["description"]) > 0
