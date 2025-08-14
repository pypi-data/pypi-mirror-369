"""Shared utilities for validation tests."""

from typing import Any

import pytest


class ValidationHelper:
    """Helper class for common validation test patterns."""

    @staticmethod
    def assert_error_response(result: dict[str, Any], context: str = "") -> None:
        """Validate that a result is a proper error response."""
        assert isinstance(result, dict), f"Expected error dict {context}"
        assert any(key in result for key in ["error", "errors", "message"]), (
            f"Error response should contain error information {context}"
        )

    @staticmethod
    def assert_pydantic_response(result: Any, expected_type: type, context: str = "") -> None:
        """Validate that a result is a proper Pydantic model response."""
        assert isinstance(result, expected_type), (
            f"Expected {expected_type.__name__}, got {type(result)} {context}"
        )

    @staticmethod
    def assert_list_field(
        obj: Any, field_name: str, expected_item_type: type | None = None
    ) -> None:
        """Validate that an object has a list field with optional item type checking."""
        assert hasattr(obj, field_name), f"Object should have {field_name} attribute"
        field_value = getattr(obj, field_name)
        assert isinstance(field_value, list), f"{field_name} should be a list"

        if expected_item_type and field_value:
            assert isinstance(field_value[0], expected_item_type), (
                f"Items in {field_name} should be {expected_item_type.__name__}"
            )

    @staticmethod
    def assert_string_field(obj: Any, field_name: str, min_length: int = 0) -> None:
        """Validate that an object has a string field with optional minimum length."""
        assert hasattr(obj, field_name), f"Object should have {field_name} attribute"
        field_value = getattr(obj, field_name)
        assert isinstance(field_value, str), f"{field_name} should be a string"
        if min_length > 0:
            assert len(field_value) >= min_length, (
                f"{field_name} should be at least {min_length} characters"
            )

    @staticmethod
    def assert_uuid_field(obj: Any, field_name: str) -> None:
        """Validate that an object has a field that looks like a UUID."""
        ValidationHelper.assert_string_field(obj, field_name, min_length=32)
        field_value = getattr(obj, field_name)
        # Basic UUID format check (allowing both with and without hyphens)
        cleaned = field_value.replace("-", "")
        assert len(cleaned) >= 32 and all(c in "0123456789abcdefABCDEF" for c in cleaned), (
            f"{field_name} should be a valid UUID format"
        )

    @staticmethod
    def validate_datetime_string(datetime_str: str, field_name: str = "datetime") -> None:
        """Validate that a string is a proper datetime format."""
        assert isinstance(datetime_str, str), f"{field_name} should be a string"
        # Check for ISO format indicators
        assert any(char in datetime_str for char in ["T", ":", "-"]), (
            f"{field_name} should be in ISO datetime format"
        )


@pytest.fixture
def validation_helper():
    """Provide validation helper for tests."""
    return ValidationHelper()
