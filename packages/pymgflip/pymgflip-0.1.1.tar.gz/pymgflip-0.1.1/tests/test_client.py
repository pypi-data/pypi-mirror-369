"""Tests for the pymgflip client."""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from pymgflip import CaptionResult, Client, Meme
from pymgflip.exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    PremiumRequiredError,
    ValidationError,
)


class TestClient:
    """Test the Client class."""

    def test_init_no_auth(self):
        """Test client initialization without auth."""
        client = Client()
        assert client.username is None
        assert client.password is None
        assert client.timeout == 30.0
        assert client.is_premium is None

    def test_init_with_auth(self):
        """Test client initialization with auth."""
        client = Client(username="testuser", password="testpass", timeout=60.0)
        assert client.username == "testuser"
        assert client.password == "testpass"
        assert client.timeout == 60.0

    def test_context_manager(self):
        """Test client as context manager."""
        with Client() as client:
            assert client._client is not None

    def test_get_memes_success(self, httpx_mock: HTTPXMock):
        """Test successful get_memes call."""
        mock_response = {
            "success": True,
            "data": {
                "memes": [
                    {
                        "id": "61579",
                        "name": "One Does Not Simply",
                        "url": "https://i.imgflip.com/1bij.jpg",
                        "width": 568,
                        "height": 335,
                        "box_count": 2,
                    },
                    {
                        "id": "101470",
                        "name": "Ancient Aliens",
                        "url": "https://i.imgflip.com/26am.jpg",
                        "width": 500,
                        "height": 437,
                        "box_count": 2,
                    },
                ]
            },
        }

        httpx_mock.add_response(
            url="https://api.imgflip.com/get_memes",
            json=mock_response,
        )

        client = Client()
        memes = client.get_memes()

        assert len(memes) == 2
        assert isinstance(memes[0], Meme)
        assert memes[0].id == "61579"
        assert memes[0].name == "One Does Not Simply"
        assert memes[1].id == "101470"

    def test_get_memes_api_error(self, httpx_mock: HTTPXMock):
        """Test get_memes with API error."""
        httpx_mock.add_response(
            url="https://api.imgflip.com/get_memes",
            json={"success": False, "error_message": "API is down"},
        )

        client = Client()
        with pytest.raises(APIError) as exc_info:
            client.get_memes()

        assert "API is down" in str(exc_info.value)

    def test_get_memes_network_error(self, httpx_mock: HTTPXMock):
        """Test get_memes with network error."""
        httpx_mock.add_exception(
            httpx.ConnectError("Connection failed"),
            url="https://api.imgflip.com/get_memes",
        )

        client = Client()
        with pytest.raises(NetworkError) as exc_info:
            client.get_memes()

        assert "Network error" in str(exc_info.value)

    def test_caption_image_success(self, httpx_mock: HTTPXMock):
        """Test successful caption_image call."""
        mock_response = {
            "success": True,
            "data": {
                "url": "https://i.imgflip.com/abc123.jpg",
                "page_url": "https://imgflip.com/i/abc123",
            },
        }

        httpx_mock.add_response(
            url="https://api.imgflip.com/caption_image",
            json=mock_response,
        )

        client = Client(username="testuser", password="testpass")
        result = client.caption_image(
            template_id="61579",
            text0="One does not simply",
            text1="Write unit tests",
        )

        assert isinstance(result, CaptionResult)
        assert result.success is True
        assert result.url == "https://i.imgflip.com/abc123.jpg"
        assert result.page_url == "https://imgflip.com/i/abc123"

    def test_caption_image_no_auth(self):
        """Test caption_image without authentication."""
        client = Client()

        with pytest.raises(AuthenticationError) as exc_info:
            client.caption_image(template_id="61579", text0="Test")

        assert "Username and password required" in str(exc_info.value)

    def test_caption_image_auth_failure(self, httpx_mock: HTTPXMock):
        """Test caption_image with invalid credentials."""
        httpx_mock.add_response(
            url="https://api.imgflip.com/caption_image",
            json={
                "success": False,
                "error_message": "Invalid username or password",
            },
        )

        client = Client(username="wrong", password="wrong")

        with pytest.raises(AuthenticationError) as exc_info:
            client.caption_image(template_id="61579", text0="Test")

        assert "Invalid username or password" in str(exc_info.value)

    def test_caption_image_premium_watermark(self, httpx_mock: HTTPXMock):
        """Test caption_image with no_watermark premium feature."""
        httpx_mock.add_response(
            url="https://api.imgflip.com/caption_image",
            json={
                "success": False,
                "error_message": "no_watermark requires a premium subscription",
            },
        )

        client = Client(username="testuser", password="testpass")

        with pytest.raises(PremiumRequiredError) as exc_info:
            client.caption_image(
                template_id="61579",
                text0="Test",
                no_watermark=True,
            )

        assert "premium subscription" in str(exc_info.value)
        assert client.is_premium is False

    def test_search_memes_premium_required(self, httpx_mock: HTTPXMock):
        """Test search_memes premium requirement."""
        httpx_mock.add_response(
            url="https://api.imgflip.com/search_memes",
            json={
                "success": False,
                "error_message": "search_memes requires a premium subscription",
            },
        )

        client = Client(username="testuser", password="testpass")

        with pytest.raises(PremiumRequiredError) as exc_info:
            client.search_memes("drake")

        assert "premium subscription" in str(exc_info.value)

    def test_automeme_premium_required(self, httpx_mock: HTTPXMock):
        """Test automeme premium requirement."""
        httpx_mock.add_response(
            url="https://api.imgflip.com/automeme",
            json={
                "success": False,
                "error_message": "automeme requires a premium subscription",
            },
        )

        client = Client(username="testuser", password="testpass")

        with pytest.raises(PremiumRequiredError) as exc_info:
            client.automeme("When the tests pass on first try")

        assert "premium subscription" in str(exc_info.value)

    def test_ai_meme_premium_required(self, httpx_mock: HTTPXMock):
        """Test ai_meme premium requirement."""
        httpx_mock.add_response(
            url="https://api.imgflip.com/ai_meme",
            json={
                "success": False,
                "error_message": "ai_meme requires a premium subscription",
            },
        )

        client = Client(username="testuser", password="testpass")

        with pytest.raises(PremiumRequiredError) as exc_info:
            client.ai_meme(prefix_text="When you realize")

        assert "premium subscription" in str(exc_info.value)

    def test_ai_meme_invalid_model(self):
        """Test ai_meme with invalid model."""
        client = Client(username="testuser", password="testpass")

        with pytest.raises(ValidationError) as exc_info:
            client.ai_meme(model="invalid_model")

        assert "Invalid parameters" in str(exc_info.value)

    def test_caption_gif_premium_required(self, httpx_mock: HTTPXMock):
        """Test caption_gif premium requirement."""
        httpx_mock.add_response(
            url="https://api.imgflip.com/caption_gif",
            json={
                "success": False,
                "error_message": "caption_gif requires a premium subscription",
            },
        )

        client = Client(username="testuser", password="testpass")

        with pytest.raises(PremiumRequiredError) as exc_info:
            client.caption_gif(
                template_id="123456",
                boxes=[{"text": "Test"}],
            )

        assert "premium subscription" in str(exc_info.value)

    def test_timeout_error(self, httpx_mock: HTTPXMock):
        """Test request timeout."""
        httpx_mock.add_exception(
            httpx.TimeoutException("Request timed out"),
            url="https://api.imgflip.com/get_memes",
        )

        client = Client(timeout=1.0)

        with pytest.raises(NetworkError) as exc_info:
            client.get_memes()

        assert "Request timed out" in str(exc_info.value)

    def test_invalid_json_response(self, httpx_mock: HTTPXMock):
        """Test handling of invalid JSON response."""
        httpx_mock.add_response(
            url="https://api.imgflip.com/get_memes",
            text="Not JSON",
            headers={"content-type": "text/plain"},
        )

        client = Client()

        with pytest.raises(APIError) as exc_info:
            client.get_memes()

        assert "Invalid JSON response" in str(exc_info.value)

    def test_http_error(self, httpx_mock: HTTPXMock):
        """Test HTTP status error."""
        httpx_mock.add_response(
            url="https://api.imgflip.com/get_memes",
            status_code=500,
            text="Internal Server Error",
        )

        client = Client()

        with pytest.raises(APIError) as exc_info:
            client.get_memes()

        assert "HTTP 500" in str(exc_info.value)
        assert exc_info.value.status_code == 500
