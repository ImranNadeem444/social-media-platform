import asyncio
import httpx
from app.core.config import settings

async def test_instagram_api():
    """Test what error Instagram returns for invalid account"""

    async with httpx.AsyncClient() as client:
        # Test with a fake account ID
        try:
            payload = {
                "image_url": "https://example.com/image.jpg",
                "caption": "test",
                "access_token": "invalid_token",
            }

            response = await client.post(
                f"https://graph.instagram.com/{settings.GRAPH_API_VERSION}/12345/media",
                json=payload,
                timeout=10.0,
            )

            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            print(f"Response JSON: {response.json()}")

            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"\nHTTPStatusError caught:")
            print(f"  str(e): '{str(e)}'")
            print(f"  e.response.status_code: {e.response.status_code}")
            print(f"  e.response.text: {e.response.text}")
            print(f"  e.response.json(): {e.response.json()}")

asyncio.run(test_instagram_api())
