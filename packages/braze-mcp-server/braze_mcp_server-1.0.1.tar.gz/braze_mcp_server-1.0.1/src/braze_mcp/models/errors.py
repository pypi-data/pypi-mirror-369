"""
Error handling for Braze MCP operations.

Provides standardized error responses with essential information for debugging
and feedback.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from .common import BrazeBaseModel


class ErrorType(StrEnum):
    """Essential error types for classification."""

    # User input errors
    VALIDATION_ERROR = "validation_error"
    INVALID_PARAMETERS = "invalid_parameters"
    FUNCTION_NOT_FOUND = "function_not_found"

    # Network/API errors
    HTTP_ERROR = "http_error"
    API_ERROR = "api_error"

    # System errors
    INTERNAL_ERROR = "internal_error"
    PARSING_ERROR = "parsing_error"
    UNEXPECTED_ERROR = "unexpected_error"


class BrazeError(BrazeBaseModel):
    """Simple error model with essential information."""

    error_type: ErrorType = Field(..., description="Type of error")
    message: str = Field(..., description="Error message")
    details: str | None = Field(None, description="Additional details")
    operation: str | None = Field(None, description="Operation that failed")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_retryable(self) -> bool:
        """Whether this error might succeed on retry."""
        return self.error_type in {ErrorType.HTTP_ERROR, ErrorType.INTERNAL_ERROR}


class ErrorResponse(BrazeBaseModel):
    """Standard error response format."""

    error: BrazeError = Field(..., description="The error that occurred")
    success: bool = Field(default=False, description="Always false for errors")

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """Include computed fields in serialization."""
        data = super().model_dump(**kwargs)
        data["retryable"] = self.error.is_retryable
        return data


# Simple factory functions for common errors


def validation_error(
    message: str, operation: str | None = None, details: str | None = None
) -> dict[str, Any]:
    """Create a validation error response."""
    error = BrazeError(
        error_type=ErrorType.VALIDATION_ERROR, message=message, details=details, operation=operation
    )
    return ErrorResponse(error=error).model_dump()


def invalid_params_error(message: str, operation: str | None = None) -> dict[str, Any]:
    """Create an invalid parameters error response."""
    error = BrazeError(
        error_type=ErrorType.INVALID_PARAMETERS, message=message, details=None, operation=operation
    )
    return ErrorResponse(error=error).model_dump()


def function_not_found_error(
    function_name: str, available_functions: list[str] | None = None
) -> dict[str, Any]:
    """Create a function not found error response."""
    details = None
    if available_functions:
        details = f"Available: {', '.join(available_functions[:5])}"
        if len(available_functions) > 5:
            details += f" and {len(available_functions) - 5} more"

    error = BrazeError(
        error_type=ErrorType.FUNCTION_NOT_FOUND,
        message=f"Function '{function_name}' not found",
        details=details,
        operation="call_function",
    )
    return ErrorResponse(error=error).model_dump()


def http_error(
    message: str, status_code: int | None = None, operation: str | None = None
) -> dict[str, Any]:
    """Create an HTTP error response."""
    details = f"HTTP {status_code}" if status_code else None
    error = BrazeError(
        error_type=ErrorType.HTTP_ERROR, message=message, details=details, operation=operation
    )
    return ErrorResponse(error=error).model_dump()


def api_error(message: str, operation: str | None = None) -> dict[str, Any]:
    """Create an API error response."""
    error = BrazeError(
        error_type=ErrorType.API_ERROR, message=message, details=None, operation=operation
    )
    return ErrorResponse(error=error).model_dump()


def internal_error(
    message: str, operation: str | None = None, exception: Exception | None = None
) -> dict[str, Any]:
    """Create an internal error response."""
    details = f"Exception: {type(exception).__name__}" if exception else None
    error = BrazeError(
        error_type=ErrorType.INTERNAL_ERROR, message=message, details=details, operation=operation
    )
    return ErrorResponse(error=error).model_dump()


def parsing_error(message: str, operation: str | None = None) -> dict[str, Any]:
    """Create a parsing error response."""
    error = BrazeError(
        error_type=ErrorType.PARSING_ERROR, message=message, details=None, operation=operation
    )
    return ErrorResponse(error=error).model_dump()


def unexpected_response_error(response_type: str, operation: str | None = None) -> dict[str, Any]:
    """Create an unexpected response error."""
    error = BrazeError(
        error_type=ErrorType.UNEXPECTED_ERROR,
        message=f"Unexpected response type: {response_type}",
        details=None,
        operation=operation,
    )
    return ErrorResponse(error=error).model_dump()
