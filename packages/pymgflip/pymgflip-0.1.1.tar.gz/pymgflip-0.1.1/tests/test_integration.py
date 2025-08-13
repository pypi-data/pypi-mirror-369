"""Integration tests for pymgflip.

These tests actually hit the Imgflip API and are skipped by default.
Run with: pytest tests/test_integration.py -m integration
"""

import os

import pytest

from pymgflip import Client


@pytest.mark.integration
class TestIntegration:
    """Integration tests that hit the real API."""

    def test_get_memes_real(self):
        """Test get_memes against real API."""
        client = Client()
        memes = client.get_memes()

        # API should return popular memes
        assert len(memes) > 0

        # Check first meme has expected fields
        first_meme = memes[0]
        assert first_meme.id
        assert first_meme.name
        assert first_meme.url
        assert first_meme.width > 0
        assert first_meme.height > 0
        assert first_meme.box_count >= 0

    @pytest.mark.skipif(
        not os.environ.get("IMGFLIP_USERNAME") or not os.environ.get("IMGFLIP_PASSWORD"),
        reason="Requires IMGFLIP_USERNAME and IMGFLIP_PASSWORD env vars",
    )
    def test_caption_image_real(self):
        """Test caption_image with real credentials if available."""
        username = os.environ.get("IMGFLIP_USERNAME")
        password = os.environ.get("IMGFLIP_PASSWORD")

        client = Client(username=username, password=password)

        # Get available memes
        memes = client.get_memes()
        assert len(memes) > 0

        # Try to caption the first meme
        result = client.caption_image(
            template_id=memes[0].id,
            text0="Testing",
            text1="pymgflip library",
        )

        # If credentials are valid, we should get a URL
        if result.success:
            assert result.url
            assert result.url.startswith("https://")
            assert "imgflip.com" in result.url
        else:
            # Credentials might be invalid
            assert result.error_message
