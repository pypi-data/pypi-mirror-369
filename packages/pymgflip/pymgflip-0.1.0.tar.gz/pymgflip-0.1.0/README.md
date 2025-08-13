# pymgflip

A type-safe Python client for the [Imgflip](https://imgflip.com) meme generation API.

## Features

- Full type hints and type safety
- Support for all Imgflip API endpoints
- Automatic handling of authentication
- Graceful handling of premium-only features  
- Comprehensive error handling
- Easy to use interface

## Installation

```bash
pip install pymgflip
```

## Quick Start

```python
from pymgflip import Client

# Get popular meme templates (no auth required)
client = Client()
memes = client.get_memes()

for meme in memes[:5]:
    print(f"{meme.name}: {meme.id}")
```

## Authentication

Most endpoints require authentication with your Imgflip account:

```python
from pymgflip import Client

client = Client(username="your_username", password="your_password")

# Create a meme
result = client.caption_image(
    template_id="61579",  # "One Does Not Simply" template
    text0="One does not simply",
    text1="Use the Imgflip API without pymgflip"
)

if result.success:
    print(f"Meme created: {result.url}")
```

## API Endpoints

### Free Endpoints

#### `get_memes()` - No authentication required
Get popular meme templates:

```python
client = Client()
memes = client.get_memes()
```

#### `caption_image()` - Requires authentication
Add captions to a meme template:

```python
client = Client(username="...", password="...")
result = client.caption_image(
    template_id="61579",
    text0="Top text",
    text1="Bottom text",
    font="impact",  # default
    max_font_size=50,
)
```

### Premium Endpoints

These endpoints require a premium Imgflip account ($9.99/month):

#### `search_memes()`
Search for meme templates:

```python
memes = client.search_memes(query="drake", include_nsfw=False)
```

#### `caption_gif()`
Caption animated GIF templates:

```python
result = client.caption_gif(
    template_id="gif_template_id",
    boxes=[
        {"text": "First frame text"},
        {"text": "Second frame text"},
    ]
)
```

#### `automeme()`
Automatically generate a meme from text:

```python
result = client.automeme(text="When the code works on the first try")
```

#### `ai_meme()`
Generate memes using AI:

```python
result = client.ai_meme(
    model="openai",  # or "classic"
    prefix_text="When you realize",
    template_id="optional_specific_template"
)
```

## Error Handling

The library provides specific exceptions for different error cases:

```python
from pymgflip import Client
from pymgflip.exceptions import (
    AuthenticationError,
    PremiumRequiredError,
    APIError,
    NetworkError
)

client = Client(username="...", password="...")

try:
    result = client.search_memes("drake")
except AuthenticationError:
    print("Invalid username or password")
except PremiumRequiredError:
    print("This feature requires a premium account")
except NetworkError:
    print("Network connection failed")
except APIError as e:
    print(f"API error: {e}")
```

## Premium Detection

The client automatically detects if an account has premium access:

```python
client = Client(username="...", password="...")

# Try to use a premium feature
try:
    client.search_memes("test")
except PremiumRequiredError:
    pass

# Check premium status
if client.is_premium is False:
    print("Account does not have premium access")
```

## Advanced Usage

### Custom Text Boxes

For advanced meme layouts with custom positioned text:

```python
result = client.caption_image(
    template_id="61579",
    boxes=[
        {
            "text": "Custom text",
            "x": 10,
            "y": 10,
            "width": 100,
            "height": 25,
            "color": "#ffffff",
            "outline_color": "#000000"
        }
    ]
)
```

### Remove Watermark (Premium)

```python
result = client.caption_image(
    template_id="61579",
    text0="Top text",
    text1="Bottom text",
    no_watermark=True  # Premium only
)
```

### Context Manager

Use the client as a context manager for automatic cleanup:

```python
with Client(username="...", password="...") as client:
    memes = client.get_memes()
    # Client automatically closes connections when done
```

## Testing

Run tests with pytest:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run unit tests
pytest

# Run integration tests (requires real API)
pytest -m integration

# Run with coverage
pytest --cov=pymgflip
```

## Environment Variables

For testing with real credentials:

```bash
export IMGFLIP_USERNAME="your_username"
export IMGFLIP_PASSWORD="your_password"
pytest tests/test_integration.py -m integration
```

## Requirements

- Python 3.8+
- httpx
- pydantic

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- [Imgflip API Documentation](https://imgflip.com/api)
- [PyPI Package](https://pypi.org/project/pymgflip/)
- [GitHub Repository](https://github.com/yourusername/pymgflip)