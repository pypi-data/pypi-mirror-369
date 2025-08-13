"""Main client for interacting with the Imgflip API."""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from pydantic import ValidationError as PydanticValidationError

from pymgflip.exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    PremiumRequiredError,
    ValidationError,
)
from pymgflip.models import (
    AIMemeRequest,
    AutoMemeRequest,
    CaptionRequest,
    CaptionResult,
    GetMemesResponse,
    Meme,
    SearchRequest,
)

logger = logging.getLogger(__name__)


class Client:
    """Client for interacting with the Imgflip API."""

    BASE_URL = "https://api.imgflip.com"

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """Initialize the Imgflip API client.

        Args:
            username: Imgflip account username (required for most endpoints)
            password: Imgflip account password (required for most endpoints)
            timeout: Request timeout in seconds
        """
        self.username = username
        self.password = password
        self.timeout = timeout
        self._is_premium: Optional[bool] = None
        self._client = httpx.Client(timeout=timeout)

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path
            params: Query parameters
            data: Form data for POST requests

        Returns:
            Parsed JSON response

        Raises:
            NetworkError: On network failures
            APIError: On API errors
        """
        url = urljoin(self.BASE_URL, endpoint)

        try:
            if method == "GET":
                response = self._client.get(url, params=params)
            elif method == "POST":
                response = self._client.post(url, data=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timed out: {e}")
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}")
        except httpx.HTTPStatusError as e:
            raise APIError(
                f"HTTP {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            )

        try:
            data = response.json()
        except ValueError as e:
            raise APIError(f"Invalid JSON response: {e}")

        # Check for API-level errors
        if isinstance(data, dict) and not data.get("success", True):
            error_msg = data.get("error_message", "Unknown API error")

            # Check for authentication errors
            if "username" in error_msg.lower() or "password" in error_msg.lower():
                raise AuthenticationError(error_msg, data)

            # Check for premium requirements
            if "premium" in error_msg.lower() or "subscription" in error_msg.lower():
                self._is_premium = False
                raise PremiumRequiredError(error_msg, data)

            raise APIError(error_msg, response_data=data)

        return data

    def _add_auth(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add authentication credentials to request data.

        Args:
            data: Request data dictionary

        Returns:
            Updated data dictionary with auth

        Raises:
            AuthenticationError: If credentials not provided
        """
        if not self.username or not self.password:
            raise AuthenticationError(
                "Username and password required for this endpoint. "
                "Initialize client with Client(username='...', password='...')"
            )

        data["username"] = self.username
        data["password"] = self.password
        return data

    def get_memes(self) -> List[Meme]:
        """Get popular meme templates.

        This is the only endpoint that doesn't require authentication.

        Returns:
            List of popular meme templates

        Raises:
            APIError: On API errors
            NetworkError: On network failures
        """
        response_data = self._make_request("GET", "/get_memes")

        try:
            response = GetMemesResponse(**response_data)
            return response.memes
        except PydanticValidationError as e:
            raise ValidationError(f"Invalid response format: {e}")

    def caption_image(
        self,
        template_id: str,
        text0: Optional[str] = None,
        text1: Optional[str] = None,
        font: str = "impact",
        max_font_size: Optional[int] = None,
        boxes: Optional[List[Dict[str, Any]]] = None,
        no_watermark: Optional[bool] = None,
    ) -> CaptionResult:
        """Add captions to a meme template.

        This requires authentication but is free with an account.

        Args:
            template_id: The template ID from get_memes()
            text0: Top text for standard memes
            text1: Bottom text for standard memes
            font: Font family (default: impact)
            max_font_size: Maximum font size in pixels
            boxes: Advanced text box positioning
            no_watermark: Remove watermark (premium only)

        Returns:
            Caption result with generated meme URL

        Raises:
            AuthenticationError: If not authenticated
            PremiumRequiredError: If no_watermark=True without premium
            ValidationError: On invalid parameters
            APIError: On API errors
        """
        try:
            request = CaptionRequest(
                template_id=template_id,
                username=self.username or "",
                password=self.password or "",
                text0=text0,
                text1=text1,
                font=font,
                max_font_size=max_font_size,
                boxes=boxes,
                no_watermark=no_watermark,
            )
        except PydanticValidationError as e:
            raise ValidationError(f"Invalid parameters: {e}")

        data = request.model_dump(exclude_none=True)
        self._add_auth(data)

        response_data = self._make_request("POST", "/caption_image", data=data)

        return CaptionResult(
            success=response_data.get("success", False),
            url=response_data.get("data", {}).get("url"),
            page_url=response_data.get("data", {}).get("page_url"),
            error_message=response_data.get("error_message"),
        )

    def caption_gif(
        self,
        template_id: str,
        boxes: List[Dict[str, Any]],
        no_watermark: Optional[bool] = None,
    ) -> CaptionResult:
        """Add captions to animated GIF templates (Premium only).

        Args:
            template_id: The GIF template ID
            boxes: Text box configurations (required for GIFs)
            no_watermark: Remove watermark

        Returns:
            Caption result with generated GIF URL

        Raises:
            PremiumRequiredError: If not a premium account
            AuthenticationError: If not authenticated
        """
        data = {
            "template_id": template_id,
            "boxes": boxes,
        }

        if no_watermark is not None:
            data["no_watermark"] = no_watermark

        self._add_auth(data)
        response_data = self._make_request("POST", "/caption_gif", data=data)

        return CaptionResult(
            success=response_data.get("success", False),
            url=response_data.get("data", {}).get("url"),
            page_url=response_data.get("data", {}).get("page_url"),
            error_message=response_data.get("error_message"),
        )

    def search_memes(
        self,
        query: str,
        include_nsfw: bool = False,
    ) -> List[Meme]:
        """Search for meme templates (Premium only).

        Args:
            query: Search query
            include_nsfw: Include NSFW results

        Returns:
            List of matching meme templates

        Raises:
            PremiumRequiredError: If not a premium account
            AuthenticationError: If not authenticated
        """
        try:
            request = SearchRequest(
                username=self.username or "",
                password=self.password or "",
                query=query,
                include_nsfw=include_nsfw,
            )
        except PydanticValidationError as e:
            raise ValidationError(f"Invalid parameters: {e}")

        data = request.model_dump(exclude_none=True)
        self._add_auth(data)

        response_data = self._make_request("POST", "/search_memes", data=data)

        memes_data = response_data.get("data", {}).get("memes", [])
        return [Meme(**meme) for meme in memes_data]

    def automeme(
        self,
        text: str,
        no_watermark: Optional[bool] = None,
    ) -> CaptionResult:
        """Automatically generate a meme from text (Premium only).

        Args:
            text: Text to generate meme from
            no_watermark: Remove watermark

        Returns:
            Generated meme result

        Raises:
            PremiumRequiredError: If not a premium account
            AuthenticationError: If not authenticated
        """
        try:
            request = AutoMemeRequest(
                username=self.username or "",
                password=self.password or "",
                text=text,
                no_watermark=no_watermark,
            )
        except PydanticValidationError as e:
            raise ValidationError(f"Invalid parameters: {e}")

        data = request.model_dump(exclude_none=True)
        self._add_auth(data)

        response_data = self._make_request("POST", "/automeme", data=data)

        return CaptionResult(
            success=response_data.get("success", False),
            url=response_data.get("data", {}).get("url"),
            page_url=response_data.get("data", {}).get("page_url"),
            error_message=response_data.get("error_message"),
        )

    def ai_meme(
        self,
        model: str = "openai",
        template_id: Optional[str] = None,
        prefix_text: Optional[str] = None,
        no_watermark: Optional[bool] = None,
    ) -> CaptionResult:
        """Generate memes using AI (Premium only).

        Args:
            model: AI model to use ("openai" or "classic")
            template_id: Optional specific template to use
            prefix_text: Optional text to start the meme with
            no_watermark: Remove watermark

        Returns:
            AI-generated meme result

        Raises:
            PremiumRequiredError: If not a premium account
            AuthenticationError: If not authenticated
            ValidationError: If invalid model specified
        """
        try:
            request = AIMemeRequest(
                username=self.username or "",
                password=self.password or "",
                model=model,
                template_id=template_id,
                prefix_text=prefix_text,
                no_watermark=no_watermark,
            )
        except PydanticValidationError as e:
            raise ValidationError(f"Invalid parameters: {e}")

        data = request.model_dump(exclude_none=True)
        self._add_auth(data)

        response_data = self._make_request("POST", "/ai_meme", data=data)

        return CaptionResult(
            success=response_data.get("success", False),
            url=response_data.get("data", {}).get("url"),
            page_url=response_data.get("data", {}).get("page_url"),
            error_message=response_data.get("error_message"),
        )

    @property
    def is_premium(self) -> Optional[bool]:
        """Check if the account is premium.

        Returns None if unknown, True/False once determined from API responses.
        """
        return self._is_premium
