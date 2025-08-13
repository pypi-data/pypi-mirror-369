from unittest.mock import patch

import pytest

from braze_mcp.registry_builder import (
    DOCSTRING_SECTION_HEADERS,
    FUNCTION_REGISTRY,
    _extract_description_from_docstring,
    _extract_param_description,
    _is_section_header,
    _log_docstring_validation_warnings,
    _parse_args_section,
    _parse_returns_section,
    _python_type_to_json_type,
    _safe_serialize_default,
    build_function_registry,
    extract_function_metadata,
    validate_docstring,
)


class TestFunctionRegistryBuilder:
    """Test the function registry auto-discovery system"""

    def test_get_campaign_list_metadata_extraction(self):
        """Test detailed metadata extraction for get_campaign_list function"""
        registry = build_function_registry()
        campaign_list_func = registry["get_campaign_list"]

        # Test function description
        assert "export a list of campaigns" in campaign_list_func["description"]

        # Test parameters structure
        params = campaign_list_func["parameters"]

        # Should have all expected parameters (including ctx)
        expected_params = {
            "ctx",
            "page",
            "include_archived",
            "sort_direction",
            "last_edit_time_gt",
        }
        assert set(params.keys()) == expected_params

        # Test page parameter
        page_param = params["page"]
        assert page_param["type"] == "integer"
        assert page_param["required"] is False
        assert page_param["default"] == 0
        assert "page" in page_param["description"].lower()

        # Test include_archived parameter
        archived_param = params["include_archived"]
        assert archived_param["type"] == "boolean"
        assert archived_param["required"] is False
        assert archived_param["default"] is False
        assert "archived" in archived_param["description"].lower()

        # Test sort_direction parameter (str with default)
        sort_param = params["sort_direction"]
        assert sort_param["type"] == "string"
        assert sort_param["required"] is False
        assert sort_param["default"] == "desc"
        assert "sort" in sort_param["description"].lower()

        # Test last_edit_time_gt parameter (Optional[str])
        time_param = params["last_edit_time_gt"]
        assert time_param["type"] == "string"
        assert time_param["required"] is False
        assert time_param["default"] is None
        assert "time" in time_param["description"].lower()

    def test_get_campaign_details_required_parameter(self):
        """Test that required parameters are correctly identified"""
        registry = build_function_registry()
        campaign_details_func = registry["get_campaign_details"]

        params = campaign_details_func["parameters"]

        # campaign_id should be required
        campaign_id_param = params["campaign_id"]
        assert campaign_id_param["required"] is True
        assert campaign_id_param["type"] == "string"
        assert "default" not in campaign_id_param  # Required params shouldn't have defaults

        # post_launch_draft_version should be optional
        draft_param = params["post_launch_draft_version"]
        assert draft_param["required"] is False
        assert draft_param["type"] == "boolean"
        assert draft_param["default"] is False


class TestMetadataExtractionHelpers:
    """Test the helper functions for metadata extraction"""

    def test_python_type_to_json_type_conversion(self):
        """Test type conversion from Python types to JSON schema types"""
        assert _python_type_to_json_type(str) == "string"
        assert _python_type_to_json_type(int) == "integer"
        assert _python_type_to_json_type(bool) == "boolean"
        assert _python_type_to_json_type(float) == "number"
        assert _python_type_to_json_type(list) == "array"
        assert _python_type_to_json_type(dict) == "object"

        # Test unknown type defaults to object
        class CustomType:
            pass

        assert _python_type_to_json_type(CustomType) == "object"

    def test_extract_description_from_docstring(self):
        """Test extracting descriptions from function docstrings"""
        # Test with proper docstring - should extract multiline description
        docstring = """Export a list of campaigns with their names.

        This function retrieves campaign data from the Braze API.

        Args:
            page: Page number
        """
        expected = "Export a list of campaigns with their names. This function retrieves campaign data from the Braze API."
        assert _extract_description_from_docstring(docstring) == expected

        # Test with None docstring
        assert _extract_description_from_docstring(None) == "No description available"

        # Test with empty docstring
        assert _extract_description_from_docstring("") == "No description available"

        # Test with whitespace-only docstring
        assert _extract_description_from_docstring("   \n   \n   ") == "No description available"

    def test_extract_param_description_from_docstring(self):
        """Test extracting parameter descriptions from docstrings (no fallback)"""
        docstring = """Function description.

        Args:
            page: Page number for pagination
            campaign_id: The unique campaign identifier
            include_archived: Whether to include archived items
        """

        # Test extracting existing parameter descriptions
        assert "pagination" in _extract_param_description(docstring, "page", int)
        assert "unique campaign identifier" in _extract_param_description(
            docstring, "campaign_id", str
        )
        assert "archived items" in _extract_param_description(docstring, "include_archived", bool)

        # Test parameter not in docstring - no fallback, just basic description
        result = _extract_param_description(docstring, "unknown_param", str)
        assert result == "Parameter unknown_param"

        # Test with no docstring
        result_no_doc = _extract_param_description(None, "some_param", str)
        assert result_no_doc == "Parameter some_param"

    def test_parse_args_section_direct(self):
        """Test the Args section parser directly"""
        docstring = """Function description.

        Args:
            simple_param: Simple description
            multi_line_param: This is a parameter with a very long description
                that spans multiple lines and should be properly joined
            type_param (str): Parameter with type annotation
            complex_param: First line
                Second line of description

        Returns:
            Something useful
        """

        # Test simple parameter
        result = _parse_args_section(docstring, "simple_param")
        assert result == "Simple description"

        # Test multi-line parameter
        result = _parse_args_section(docstring, "multi_line_param")
        assert "very long description that spans multiple lines" in result

        # Test parameter with type annotation
        result = _parse_args_section(docstring, "type_param")
        assert "Parameter with type annotation" in result

        # Test complex multi-line
        result = _parse_args_section(docstring, "complex_param")
        assert "First line Second line of description" in result

        # Test parameter not found
        result = _parse_args_section(docstring, "missing_param")
        assert result is None

        # Test with no Args section
        no_args_docstring = """Just a description.

        Returns:
            Something
        """
        result = _parse_args_section(no_args_docstring, "any_param")
        assert result is None

    def test_parse_returns_section(self):
        """Test the Returns section parser"""
        # Test with Returns section
        docstring_returns = """Function description.

        Args:
            param: Some parameter

        Returns:
            JSON string containing the response data
        """
        result = _parse_returns_section(docstring_returns)
        assert result == "JSON string containing the response data"

        # Test with multi-line Returns
        docstring_multiline = """Function description.

        Returns:
            A complex response object containing multiple fields
            and detailed information about the operation
        """
        result = _parse_returns_section(docstring_multiline)
        assert "complex response object" in result
        assert "detailed information" in result

        # Test with Return (singular)
        docstring_return = """Function description.

        Return:
            Simple return value
        """
        result = _parse_returns_section(docstring_return)
        assert result == "Simple return value"

        # Test with no Returns section
        docstring_no_returns = """Function description.

        Args:
            param: Some parameter
        """
        result = _parse_returns_section(docstring_no_returns)
        assert result is None

        # Test with None docstring
        result = _parse_returns_section(None)
        assert result is None

    def test_function_registry_includes_returns_metadata(self):
        """Test that function registry includes returns information"""
        registry = build_function_registry()

        # Check that functions have returns metadata
        for func_name in [
            "get_campaign_list",
            "get_campaign_details",
            "get_custom_attributes",
        ]:
            func_info = registry[func_name]

            # Should have returns information
            assert "returns" in func_info
            returns_info = func_info["returns"]

            # Returns should have description and type
            assert "description" in returns_info
            assert "type" in returns_info
            assert returns_info["type"] == "object"

            # Description should contain meaningful content about structured data
            description_lower = returns_info["description"].lower()
            assert any(
                keyword in description_lower
                for keyword in ["dict", "dictionary", "data", "containing"]
            )
            assert len(returns_info["description"]) > 10  # Should be descriptive

    def test_optional_type_handling(self):
        """Test that modern union types are handled correctly"""
        # Test modern optional syntax
        result = _python_type_to_json_type(str | None)
        assert result == "string"

        # Test modern union syntax
        result = _python_type_to_json_type(str | int)
        assert result == "string"

        # Test modern int | None syntax
        result = _python_type_to_json_type(int | None)
        assert result == "integer"

    def test_registry_is_built_on_import(self):
        """Test that FUNCTION_REGISTRY is automatically built on import"""
        # The registry should be populated when the module is imported
        assert isinstance(FUNCTION_REGISTRY, dict)
        assert len(FUNCTION_REGISTRY) > 0

        # Should contain our expected functions
        expected_functions = {
            "get_campaign_list",
            "get_campaign_details",
            "get_custom_attributes",
        }
        assert expected_functions.issubset(set(FUNCTION_REGISTRY.keys()))


class TestEnhancedTypeConversion:
    """Test enhanced type conversion functionality"""

    def test_context_type_handling(self):
        """Test that Context type is properly converted to object"""
        from mcp.server.fastmcp import Context

        result = _python_type_to_json_type(Context)
        assert result == "object"

    def test_generic_list_types(self):
        """Test List and generic array types"""
        result = _python_type_to_json_type(list[str])
        assert result == "array"

        result = _python_type_to_json_type(list)
        assert result == "array"

    def test_generic_dict_types(self):
        """Test Dict and generic object types"""
        result = _python_type_to_json_type(dict[str, str])
        assert result == "object"

        result = _python_type_to_json_type(dict)
        assert result == "object"

    def test_complex_union_types(self):
        """Test complex union type handling with modern syntax"""
        # Test modern str | int syntax
        result = _python_type_to_json_type(str | int)
        assert result == "string"

        # Test modern int | str | None syntax
        result = _python_type_to_json_type(int | str | None)
        assert result == "integer"

    def test_response_model_types(self):
        """Test that Response/Request/Model classes are treated as objects"""

        class TestResponse:
            pass

        class CustomRequest:
            pass

        class SomeModel:
            pass

        assert _python_type_to_json_type(TestResponse) == "object"
        assert _python_type_to_json_type(CustomRequest) == "object"
        assert _python_type_to_json_type(SomeModel) == "object"

    def test_type_conversion_error_handling(self):
        """Test that type conversion handles errors gracefully"""

        # Create a problematic type that might cause errors
        class ProblematicType:
            def __getattr__(self, name):
                raise AttributeError("Simulated error")

        result = _python_type_to_json_type(ProblematicType)
        assert result == "object"  # Should fall back to object


class TestSafeDefaultSerialization:
    """Test safe default value serialization"""

    def test_json_serializable_defaults(self):
        """Test that JSON-serializable defaults pass through unchanged"""
        assert _safe_serialize_default(42) == 42
        assert _safe_serialize_default("hello") == "hello"
        assert _safe_serialize_default(True) is True
        assert _safe_serialize_default(None) is None
        assert _safe_serialize_default([1, 2, 3]) == [1, 2, 3]
        assert _safe_serialize_default({"key": "value"}) == {"key": "value"}

    def test_function_defaults(self):
        """Test that function defaults are converted to strings"""

        def sample_func():
            pass

        result = _safe_serialize_default(sample_func)
        assert result == "<function: sample_func>"

    def test_object_defaults(self):
        """Test that complex object defaults are converted to strings"""

        class TestClass:
            def __str__(self):
                return "test_instance"

        obj = TestClass()
        result = _safe_serialize_default(obj)
        assert result == "<TestClass: test_instance>"

    def test_non_serializable_defaults(self):
        """Test handling of various non-serializable types"""
        import datetime

        # Test datetime object
        dt = datetime.datetime.now()
        result = _safe_serialize_default(dt)
        assert isinstance(result, str)
        assert "datetime" in result.lower()


class TestRobustParameterMatching:
    """Test enhanced parameter matching in docstrings"""

    def test_exact_parameter_matching(self):
        """Test that parameter matching is exact and doesn't match substrings"""
        docstring = """Function description.

        Args:
            sort_direction: Main sort parameter
            sort_direction_other: Another sort parameter
            direction: Simple direction
        """

        # Should match exact parameter name only
        result = _parse_args_section(docstring, "sort_direction")
        assert result == "Main sort parameter"

        # Should not match partial names
        result = _parse_args_section(docstring, "sort")
        assert result is None

    def test_parameter_with_type_annotations(self):
        """Test parameter parsing with type annotations in docstring"""
        docstring = """Function description.

        Args:
            param_name (str): Description with type annotation
            another_param (Optional[int]): Another parameter with complex type
            simple_param: Parameter without type annotation
        """

        result = _parse_args_section(docstring, "param_name")
        assert result == "Description with type annotation"

        result = _parse_args_section(docstring, "another_param")
        assert result == "Another parameter with complex type"

        result = _parse_args_section(docstring, "simple_param")
        assert result == "Parameter without type annotation"

    def test_dynamic_indentation_handling(self):
        """Test that indentation detection works with various formatting"""
        docstring = """Function description.

        Args:
            param1: Description that continues
                on multiple lines with proper
                indentation handling
            param2: Another parameter
        """

        result = _parse_args_section(docstring, "param1")
        expected = "Description that continues on multiple lines with proper indentation handling"
        assert result == expected


class TestErrorHandling:
    """Test enhanced error handling throughout the pipeline"""

    def test_extract_metadata_with_type_hint_errors(self):
        """Test that type hint errors don't crash metadata extraction"""

        # Create a mock function with problematic type hints
        def problematic_func(param: "NonExistentType") -> str:  # noqa: F821  # Forward ref that doesn't exist
            """Test function with bad type hints.

            Args:
                param: A parameter with problematic type

            Returns:
                A string
            """
            return "test"

        with patch("braze_mcp.registry_builder.logger.warning") as mock_warning:
            metadata = extract_function_metadata(problematic_func)

            # Should have warning about type hints but still extract metadata
            mock_warning.assert_called()
            assert any(
                "Could not get type hints" in str(call) for call in mock_warning.call_args_list
            )

            # Should still have basic metadata
            assert metadata["description"] == "Test function with bad type hints."
            assert "param" in metadata["parameters"]
            assert metadata["parameters"]["param"]["type"] == "string"  # fallback

    def test_extract_metadata_with_parameter_errors(self):
        """Test that individual parameter errors don't break entire extraction"""

        def func_with_issues(normal_param: str, problematic_param) -> str:
            """Function with mixed parameter issues.

            Args:
                normal_param: This is fine
                # Missing problematic_param description

            Returns:
                A string
            """
            return "test"

        metadata = extract_function_metadata(func_with_issues)

        # Should have metadata for both parameters
        assert "normal_param" in metadata["parameters"]
        assert "problematic_param" in metadata["parameters"]

        # Normal param should have proper description
        assert "This is fine" in metadata["parameters"]["normal_param"]["description"]

        # Problematic param should have fallback description
        assert (
            "Parameter problematic_param"
            == metadata["parameters"]["problematic_param"]["description"]
        )

    def test_extract_metadata_complete_failure(self):
        """Test that complete metadata extraction failures are handled"""

        # Create an object that looks like a function but will cause errors
        class NotAFunction:
            __name__ = "fake_function"

        fake_func = NotAFunction()

        with patch("builtins.print") as mock_print:
            metadata = extract_function_metadata(fake_func)

            # Should have error message
            error_calls = [call for call in mock_print.call_args_list if "Error" in str(call)]
            assert len(error_calls) > 0

            # Should return minimal metadata with error info
            assert metadata["description"] == "Function fake_function (metadata extraction failed)"
            assert metadata["parameters"] == {}
            assert "error" in metadata


class TestMultilineDescriptions:
    """Test the enhanced multiline description extraction"""

    def test_multiline_description_extraction(self):
        """Test that multiline descriptions are properly extracted"""
        docstring = """Create a new campaign in Braze.

        This function allows you to create campaigns with various settings
        and configurations for targeted messaging. It provides comprehensive
        control over campaign parameters.

        Args:
            param: Some parameter
        """

        result = _extract_description_from_docstring(docstring)
        expected = (
            "Create a new campaign in Braze. This function allows you to create "
            "campaigns with various settings and configurations for targeted messaging. "
            "It provides comprehensive control over campaign parameters."
        )
        assert result == expected

    def test_description_stops_at_sections(self):
        """Test that description extraction stops at section headers"""
        docstring = """Main description line.

        Continued description here.

        Args:
            This should not be in description
        """

        result = _extract_description_from_docstring(docstring)
        assert result == "Main description line. Continued description here."
        assert "Args:" not in result
        assert "This should not be in description" not in result

    def test_description_handles_various_sections(self):
        """Test that description stops at various section types"""
        sections = ["Args:", "Returns:", "Raises:", "Examples:", "Note:", "Warning:"]

        for section in sections:
            docstring = f"""Main description.

            More description content.

            {section}
                Section content here
            """

            result = _extract_description_from_docstring(docstring)
            assert result == "Main description. More description content."
            assert section not in result


class TestDocstringValidation:
    """Test the docstring validation system"""

    def test_valid_docstring(self):
        """Test that a properly formatted docstring passes validation"""

        def good_function(ctx, param1: str, param2: int = 0) -> dict:
            """Brief description of the function.

            Args:
                param1: Description of param1
                param2: Description of param2 with default

            Returns:
                Dictionary containing result data
            """
            pass

        is_valid, issues = validate_docstring(good_function)
        assert is_valid
        assert len(issues) == 0

    def test_missing_docstring(self):
        """Test that missing docstring is caught"""

        def bad_function(ctx, param1: str) -> dict:
            pass

        is_valid, issues = validate_docstring(bad_function)
        assert not is_valid
        assert "Missing docstring" in issues

    def test_missing_args_section(self):
        """Test that missing Args section is caught"""

        def bad_function(ctx, param1: str, param2: int) -> dict:
            """Function description without Args section."""
            pass

        is_valid, issues = validate_docstring(bad_function)
        assert not is_valid
        assert any("Args" in issue for issue in issues)

    def test_undocumented_parameter(self):
        """Test that undocumented parameters are caught"""

        def bad_function(ctx, param1: str, param2: int) -> dict:
            """Function description.

            Args:
                param1: Documented parameter
                # param2 is missing!
            """
            pass

        is_valid, issues = validate_docstring(bad_function)
        assert not is_valid
        assert any("param2" in issue for issue in issues)

    def test_ctx_parameter_ignored(self):
        """Test that ctx parameter doesn't need documentation"""

        def bad_function(ctx) -> dict:
            """Function that only takes ctx parameter."""
            pass

        is_valid, issues = validate_docstring(bad_function)
        assert not is_valid  # Returns section is still required
        assert "Missing Returns section" in issues

        def good_function(ctx) -> dict:
            """Function that only takes ctx parameter.

            Returns:
                Dictionary containing result data
            """
            pass

        is_valid, issues = validate_docstring(good_function)
        assert is_valid  # ctx-only functions don't need Args section but do need Returns

    def test_missing_returns_section(self):
        """Test that missing Returns section is caught"""

        def bad_function(ctx, param1: str) -> dict:
            """Function description.

            Args:
                param1: Documented parameter
            """
            pass

        is_valid, issues = validate_docstring(bad_function)
        assert not is_valid
        assert "Missing Returns section" in issues

    def test_empty_returns_section(self):
        """Test that empty Returns section is caught"""

        def bad_function(ctx, param1: str) -> dict:
            """Function description.

            Args:
                param1: Documented parameter

            Returns:
            """
            pass

        is_valid, issues = validate_docstring(bad_function)
        assert not is_valid
        assert "Returns section must contain a description" in issues

    def test_validation_logging(self, caplog):
        """Test that validation warnings are logged properly"""

        def bad_function(ctx, param1: str) -> dict:
            """Bad function."""
            pass

        is_valid, issues = validate_docstring(bad_function)
        _log_docstring_validation_warnings("test_function", issues)

        assert "Docstring issues in function 'test_function':" in caplog.text
        assert "Consider following the docstring conventions" in caplog.text

    def test_strict_validation_in_registry_building(self):
        """Test that functions with invalid docstrings fail to register in strict mode"""
        from types import ModuleType

        # Create a temporary module
        temp_module = ModuleType("temp_tools")
        temp_module.__name__ = "braze_mcp.tools.temp"
        temp_module.__register_mcp_tools__ = True

        # Add a function with invalid docstring
        async def bad_tool_function(ctx, param1: str) -> dict:
            """Function without Args section."""
            return {}

        # Set the module attribute so it looks like it belongs to tools
        bad_tool_function.__module__ = "braze_mcp.tools.temp"
        temp_module.get_bad_tool = bad_tool_function

        # Patch the discovery function to include our bad module
        with patch(
            "braze_mcp.registry_builder._discover_mcp_tool_modules",
            return_value=[temp_module],
        ):
            # This should raise an error due to strict validation
            with pytest.raises(ValueError, match="has invalid docstring and cannot be registered"):
                build_function_registry()


class TestSectionHeaderDetection:
    """Test the _is_section_header helper function"""

    def test_basic_section_header_detection(self):
        """Test basic section header detection without specific sections"""
        # Valid section headers
        assert _is_section_header("Args:")
        assert _is_section_header("Returns:")
        assert _is_section_header("Notes:")
        assert _is_section_header("Custom Section:")

        # Invalid - indented
        assert not _is_section_header("    Args:")
        assert not _is_section_header("\tReturns:")

        # Invalid - no colon
        assert not _is_section_header("Args")
        assert not _is_section_header("Returns")

        # Invalid - empty or whitespace
        assert not _is_section_header("")
        assert not _is_section_header("   ")

    def test_specific_section_validation(self):
        """Test section header detection with specific valid sections"""
        valid_sections = ["args:", "returns:", "notes:"]

        # Valid sections
        assert _is_section_header("Args:", valid_sections)
        assert _is_section_header("ARGS:", valid_sections)  # Case insensitive
        assert _is_section_header("returns:", valid_sections)
        assert _is_section_header("Notes:", valid_sections)

        # Invalid sections (not in list)
        assert not _is_section_header("Examples:", valid_sections)
        assert not _is_section_header("Custom:", valid_sections)

        # Still invalid for basic formatting reasons
        assert not _is_section_header("    args:", valid_sections)
        assert not _is_section_header("args", valid_sections)

    def test_docstring_section_headers_validation(self):
        """Test with the actual DOCSTRING_SECTION_HEADERS list"""
        # Valid headers from the constant
        assert _is_section_header("Args:", DOCSTRING_SECTION_HEADERS)
        assert _is_section_header("Arguments:", DOCSTRING_SECTION_HEADERS)
        assert _is_section_header("Parameters:", DOCSTRING_SECTION_HEADERS)
        assert _is_section_header("Returns:", DOCSTRING_SECTION_HEADERS)
        assert _is_section_header("Return:", DOCSTRING_SECTION_HEADERS)
        assert _is_section_header("Raises:", DOCSTRING_SECTION_HEADERS)
        assert _is_section_header("Examples:", DOCSTRING_SECTION_HEADERS)

        # Case insensitive
        assert _is_section_header("ARGS:", DOCSTRING_SECTION_HEADERS)
        assert _is_section_header("returns:", DOCSTRING_SECTION_HEADERS)

        # Invalid header
        assert not _is_section_header("Custom:", DOCSTRING_SECTION_HEADERS)

    def test_real_docstring_scenarios(self):
        """Test with realistic docstring line scenarios"""
        # Typical docstring lines that should be detected as headers
        assert _is_section_header("Args:")
        assert _is_section_header("Returns:")

        # Should NOT be detected as headers (indented)
        assert not _is_section_header("    Returns:")
        assert not _is_section_header("\tArgs:")

        # Parameter descriptions (should not be headers)
        assert not _is_section_header("    param1: Description of parameter")
        assert not _is_section_header("        campaign_id: The campaign identifier")

        # Regular text (should not be headers)
        assert not _is_section_header("This is a regular description line.")
        assert not _is_section_header("Some text with a colon: but indented")
