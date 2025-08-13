#!/usr/bin/env python3
"""Basic usage examples for pymgflip."""

import os
from pymgflip import Client
from pymgflip.exceptions import AuthenticationError, PremiumRequiredError


def example_get_memes():
    """Example: Get popular meme templates."""
    print("=== Getting popular memes (no auth required) ===")
    
    client = Client()
    memes = client.get_memes()
    
    print(f"Found {len(memes)} popular meme templates\n")
    
    # Show first 5 memes
    for meme in memes[:5]:
        print(f"ID: {meme.id}")
        print(f"Name: {meme.name}")
        print(f"URL: {meme.url}")
        print(f"Size: {meme.width}x{meme.height}")
        print(f"Text boxes: {meme.box_count}")
        print("-" * 40)
    
    return memes


def example_caption_image(username: str, password: str, template_id: str):
    """Example: Create a meme with captions."""
    print("\n=== Creating a meme with captions ===")
    
    client = Client(username=username, password=password)
    
    try:
        result = client.caption_image(
            template_id=template_id,
            text0="When you finally",
            text1="Get the API working",
        )
        
        if result.success:
            print(f"✅ Meme created successfully!")
            print(f"URL: {result.url}")
            print(f"Page: {result.page_url}")
        else:
            print(f"❌ Failed: {result.error_message}")
            
    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_premium_features(username: str, password: str):
    """Example: Try to use premium features."""
    print("\n=== Testing premium features ===")
    
    client = Client(username=username, password=password)
    
    # Try search (premium only)
    try:
        print("Attempting to search for 'drake' memes...")
        memes = client.search_memes("drake")
        print(f"✅ Found {len(memes)} Drake memes (account has premium!)")
        
    except PremiumRequiredError:
        print("❌ Search requires premium subscription")
        print(f"Premium status: {client.is_premium}")
    
    # Try AI meme (premium only)
    try:
        print("\nAttempting to generate AI meme...")
        result = client.ai_meme(prefix_text="That feeling when")
        if result.success:
            print(f"✅ AI meme created: {result.url}")
            
    except PremiumRequiredError:
        print("❌ AI memes require premium subscription")


def main():
    """Run examples."""
    print("pymgflip Usage Examples")
    print("=" * 50)
    
    # Get popular memes (no auth needed)
    memes = example_get_memes()
    
    # Check for credentials
    username = os.environ.get("IMGFLIP_USERNAME")
    password = os.environ.get("IMGFLIP_PASSWORD")
    
    if username and password:
        # Use first meme as template
        if memes:
            example_caption_image(username, password, memes[0].id)
        
        # Test premium features
        example_premium_features(username, password)
    else:
        print("\n⚠️  Set IMGFLIP_USERNAME and IMGFLIP_PASSWORD environment variables")
        print("   to test authenticated features.")


if __name__ == "__main__":
    main()