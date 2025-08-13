"""pymgflip - A type-safe Python client for the Imgflip meme generation API."""

from pymgflip.client import Client
from pymgflip.exceptions import (
    APIError,
    AuthenticationError,
    PremiumRequiredError,
    PymgflipError,
)
from pymgflip.models import CaptionResult, Meme

__version__ = "0.1.0"
__all__ = [
    "Client",
    "PymgflipError",
    "AuthenticationError",
    "PremiumRequiredError",
    "APIError",
    "Meme",
    "CaptionResult",
]
