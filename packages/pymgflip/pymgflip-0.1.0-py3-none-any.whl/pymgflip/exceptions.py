"""Exception classes for pymgflip."""

from typing import Any, Dict, Optional


class PymgflipError(Exception):
    """Base exception for all pymgflip errors."""

    def __init__(self, message: str, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.response_data = response_data


class AuthenticationError(PymgflipError):
    """Raised when authentication fails."""


class PremiumRequiredError(PymgflipError):
    """Raised when trying to use a premium feature without a premium account."""


class APIError(PymgflipError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, response_data)
        self.status_code = status_code


class ValidationError(PymgflipError):
    """Raised when input validation fails."""


class NetworkError(PymgflipError):
    """Raised when network operations fail."""
