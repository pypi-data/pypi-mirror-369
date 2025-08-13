"""Tests for pymgflip models."""

import pytest
from pydantic import ValidationError

from pymgflip.models import (
    AIMemeRequest,
    CaptionRequest,
    CaptionResult,
    GetMemesResponse,
    Meme,
    TextBox,
)


class TestMeme:
    """Test the Meme model."""

    def test_valid_meme(self):
        """Test creating a valid Meme."""
        meme = Meme(
            id="61579",
            name="One Does Not Simply",
            url="https://i.imgflip.com/1bij.jpg",
            width=568,
            height=335,
            box_count=2,
        )

        assert meme.id == "61579"
        assert meme.name == "One Does Not Simply"
        assert meme.url == "https://i.imgflip.com/1bij.jpg"
        assert meme.width == 568
        assert meme.height == 335
        assert meme.box_count == 2
        assert meme.captions is None

    def test_meme_with_captions(self):
        """Test Meme with captions field."""
        meme = Meme(
            id="61579",
            name="Test",
            url="https://example.com/test.jpg",
            width=100,
            height=100,
            box_count=2,
            captions=1000,
        )

        assert meme.captions == 1000

    def test_invalid_meme_missing_fields(self):
        """Test Meme with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            Meme(id="123", name="Test")

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("url",) for e in errors)
        assert any(e["loc"] == ("width",) for e in errors)


class TestGetMemesResponse:
    """Test the GetMemesResponse model."""

    def test_successful_response(self):
        """Test successful GetMemesResponse."""
        response = GetMemesResponse(
            success=True,
            data={
                "memes": [
                    {
                        "id": "61579",
                        "name": "One Does Not Simply",
                        "url": "https://i.imgflip.com/1bij.jpg",
                        "width": 568,
                        "height": 335,
                        "box_count": 2,
                    }
                ]
            },
        )

        assert response.success is True
        memes = response.memes
        assert len(memes) == 1
        assert memes[0].id == "61579"

    def test_empty_response(self):
        """Test GetMemesResponse with no data."""
        response = GetMemesResponse(success=False)

        assert response.success is False
        assert response.data is None
        assert response.memes == []

    def test_response_without_memes_key(self):
        """Test GetMemesResponse with data but no memes key."""
        response = GetMemesResponse(success=True, data={"other": "data"})

        assert response.memes == []


class TestCaptionResult:
    """Test the CaptionResult model."""

    def test_successful_result(self):
        """Test successful CaptionResult."""
        result = CaptionResult(
            success=True,
            url="https://i.imgflip.com/abc123.jpg",
            page_url="https://imgflip.com/i/abc123",
        )

        assert result.success is True
        assert result.url == "https://i.imgflip.com/abc123.jpg"
        assert result.page_url == "https://imgflip.com/i/abc123"
        assert result.error_message is None

    def test_failed_result(self):
        """Test failed CaptionResult."""
        result = CaptionResult(
            success=False,
            error_message="Invalid template ID",
        )

        assert result.success is False
        assert result.url is None
        assert result.error_message == "Invalid template ID"


class TestCaptionRequest:
    """Test the CaptionRequest model."""

    def test_minimal_request(self):
        """Test CaptionRequest with minimal fields."""
        request = CaptionRequest(
            template_id="61579",
            username="testuser",
            password="testpass",
        )

        assert request.template_id == "61579"
        assert request.username == "testuser"
        assert request.password == "testpass"
        assert request.font == "impact"
        assert request.text0 is None
        assert request.text1 is None

    def test_full_request(self):
        """Test CaptionRequest with all fields."""
        request = CaptionRequest(
            template_id="61579",
            username="testuser",
            password="testpass",
            text0="Top text",
            text1="Bottom text",
            font="arial",
            max_font_size=50,
            no_watermark=True,
        )

        assert request.text0 == "Top text"
        assert request.text1 == "Bottom text"
        assert request.font == "arial"
        assert request.max_font_size == 50
        assert request.no_watermark is True


class TestAIMemeRequest:
    """Test the AIMemeRequest model."""

    def test_default_model(self):
        """Test AIMemeRequest with default model."""
        request = AIMemeRequest(
            username="testuser",
            password="testpass",
        )

        assert request.model == "openai"

    def test_classic_model(self):
        """Test AIMemeRequest with classic model."""
        request = AIMemeRequest(
            username="testuser",
            password="testpass",
            model="classic",
        )

        assert request.model == "classic"

    def test_invalid_model(self):
        """Test AIMemeRequest with invalid model."""
        with pytest.raises(ValidationError) as exc_info:
            AIMemeRequest(
                username="testuser",
                password="testpass",
                model="invalid",
            )

        errors = exc_info.value.errors()
        assert any("string_pattern_mismatch" in str(e) for e in errors)


class TestTextBox:
    """Test the TextBox model."""

    def test_minimal_textbox(self):
        """Test TextBox with minimal fields."""
        box = TextBox(text="Hello World")

        assert box.text == "Hello World"
        assert box.x is None
        assert box.y is None
        assert box.width is None
        assert box.height is None
        assert box.color is None
        assert box.outline_color is None

    def test_full_textbox(self):
        """Test TextBox with all fields."""
        box = TextBox(
            text="Hello World",
            x=10,
            y=20,
            width=100,
            height=50,
            color="#ffffff",
            outline_color="#000000",
        )

        assert box.x == 10
        assert box.y == 20
        assert box.width == 100
        assert box.height == 50
        assert box.color == "#ffffff"
        assert box.outline_color == "#000000"
