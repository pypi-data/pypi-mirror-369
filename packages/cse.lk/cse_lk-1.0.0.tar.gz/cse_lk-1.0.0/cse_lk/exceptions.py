"""Custom exceptions for the CSE API client."""

from typing import Optional, Any, Dict


class CSEError(Exception):
    """Base exception for all CSE API related errors."""

    def __init__(
        self, message: str, response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.response_data = response_data or {}


class CSEAPIError(CSEError):
    """Raised when the CSE API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, response_data)
        self.status_code = status_code


class CSENetworkError(CSEError):
    """Raised when there's a network-related error accessing the CSE API."""

    pass


class CSEValidationError(CSEError):
    """Raised when input validation fails."""

    pass


class CSEAuthenticationError(CSEError):
    """Raised when authentication fails."""

    pass


class CSERateLimitError(CSEError):
    """Raised when API rate limits are exceeded."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, response_data)
        self.retry_after = retry_after
