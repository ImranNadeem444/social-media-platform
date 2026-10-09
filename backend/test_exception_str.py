import asyncio
import httpx
from app.services.instagram_publish import publish_to_instagram
from app.services.encryption import encrypt_token

async def test():
    """Test what exception string looks like"""

    # Use a fake token
    fake_token = "fake_token_12345"
    encrypted_token = encrypt_token(fake_token)

    try:
        await publish_to_instagram(
            instagram_account_id="12345",
            image_url="https://example.com/image.jpg",
            caption="test",
            encrypted_token=encrypted_token,
        )
    except Exception as e:
        print(f"Exception type: {type(e).__name__}")
        print(f"Exception repr: {repr(e)}")
        print(f"Exception str: '{str(e)}'")
        print(f"Exception str length: {len(str(e))}")
        print(f"Exception str is empty: {str(e) == ''}")

        # Check if it has a response attribute
        if hasattr(e, 'response'):
            print(f"\nException has response attribute:")
            print(f"  Status: {e.response.status_code}")
            print(f"  Response text: {e.response.text[:200]}")

asyncio.run(test())
