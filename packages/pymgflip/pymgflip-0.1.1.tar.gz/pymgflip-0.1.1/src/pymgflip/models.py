"""Data models for pymgflip API responses."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Meme(BaseModel):
    """Represents a meme template."""

    id: str
    name: str
    url: str
    width: int
    height: int
    box_count: int
    captions: Optional[int] = None


class GetMemesResponse(BaseModel):
    """Response from /get_memes endpoint."""

    success: bool
    data: Optional[Dict[str, Any]] = None

    @property
    def memes(self) -> List[Meme]:
        """Extract memes from response data."""
        if self.data and "memes" in self.data:
            return [Meme(**meme) for meme in self.data["memes"]]
        return []


class CaptionResult(BaseModel):
    """Result of a caption operation."""

    success: bool
    url: Optional[str] = None
    page_url: Optional[str] = None
    error_message: Optional[str] = None


class TextBox(BaseModel):
    """Represents a text box for meme captioning."""

    text: str
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    color: Optional[str] = None
    outline_color: Optional[str] = None


class CaptionRequest(BaseModel):
    """Request parameters for caption_image endpoint."""

    template_id: str
    username: str
    password: str
    text0: Optional[str] = None
    text1: Optional[str] = None
    font: Optional[str] = Field(default="impact")
    max_font_size: Optional[int] = None
    boxes: Optional[List[Dict[str, Any]]] = None
    no_watermark: Optional[bool] = None


class SearchRequest(BaseModel):
    """Request parameters for search_memes endpoint."""

    username: str
    password: str
    query: str
    include_nsfw: Optional[bool] = False


class AutoMemeRequest(BaseModel):
    """Request parameters for automeme endpoint."""

    username: str
    password: str
    text: str
    no_watermark: Optional[bool] = None


class AIMemeRequest(BaseModel):
    """Request parameters for ai_meme endpoint."""

    username: str
    password: str
    model: Optional[str] = Field(default="openai", pattern="^(openai|classic)$")
    template_id: Optional[str] = None
    prefix_text: Optional[str] = None
    no_watermark: Optional[bool] = None
