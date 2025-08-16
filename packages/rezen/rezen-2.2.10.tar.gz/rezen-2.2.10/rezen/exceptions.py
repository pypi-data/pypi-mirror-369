"""Custom exceptions for the ReZEN API wrapper."""

from typing import Any, Dict, List, Optional


class RezenError(Exception):
    """Base exception for all ReZEN API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize ReZEN error.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
            response_data: Response data from API if available
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationError(RezenError):
    """Raised when authentication fails."""

    pass


class ValidationError(RezenError):
    """Raised when request validation fails."""

    pass


class NotFoundError(RezenError):
    """Raised when a resource is not found."""

    pass


class RateLimitError(RezenError):
    """Raised when rate limit is exceeded."""

    pass


class ServerError(RezenError):
    """Raised when server returns 5xx error."""

    pass


class NetworkError(RezenError):
    """Raised when network connection fails."""

    pass


class TransactionSequenceError(ValidationError):
    """Raised when transaction builder operations are called in wrong sequence."""

    def __init__(
        self, message: str, required_steps: Optional[List[str]] = None
    ) -> None:
        """Initialize transaction sequence error.

        Args:
            message: Error message
            required_steps: List of required steps in order
        """
        if required_steps:
            steps_str = "\n".join(
                f"{i+1}. {step}" for i, step in enumerate(required_steps)
            )
            message = f"{message}\n\nRequired sequence:\n{steps_str}"
        super().__init__(message)
        self.required_steps = required_steps


class InvalidFieldNameError(ValidationError):
    """Raised when incorrect field names are used."""

    def __init__(
        self, field_name: str, correct_name: str, additional_info: str = ""
    ) -> None:
        """Initialize invalid field name error.

        Args:
            field_name: The incorrect field name used
            correct_name: The correct field name to use
            additional_info: Additional context about the field
        """
        message = f"Invalid field name '{field_name}'. Use '{correct_name}' instead."
        if additional_info:
            message += f" {additional_info}"
        super().__init__(message)
        self.field_name = field_name
        self.correct_name = correct_name


class InvalidFieldValueError(ValidationError):
    """Raised when field values don't match expected format."""

    def __init__(self, field_name: str, value: Any, expected_format: str) -> None:
        """Initialize invalid field value error.

        Args:
            field_name: The field with invalid value
            value: The invalid value provided
            expected_format: Description of expected format
        """
        message = (
            f"Invalid value for '{field_name}': {value}. Expected: {expected_format}"
        )
        super().__init__(message)
        self.field_name = field_name
        self.value = value
        self.expected_format = expected_format
