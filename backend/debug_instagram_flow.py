"""
Debug the Instagram publishing flow to see exactly where it fails.
"""
import asyncio
from app.services.instagram_publish import publish_to_instagram
from app.services.encryption import encrypt_token, decrypt_token
from app.core.config import settings

async def test_flow():
    # First, let's check what we're using to authenticate
    print("Testing Instagram publishing flow with actual token from production...\n")

    # Get the first user's Instagram token from the database
    from app.db.database import SessionLocal
    from app.models.social_account import SocialAccount
    from sqlalchemy import select

    db = SessionLocal()
    social_account = db.scalar(
        select(SocialAccount).where(SocialAccount.platform == "instagram").limit(1)
    )

    if not social_account:
        print("No Instagram account found in database")
        return

    print(f"Found account: {social_account.account_name} (ID: {social_account.account_id})")

    # Decrypt the token
    try:
        access_token = decrypt_token(social_account.access_token_encrypted)
        print(f"Token decrypted successfully")
        print(f"Token length: {len(access_token)}")
        print(f"Token preview: {access_token[:20]}...\n")
    except Exception as e:
        print(f"ERROR decrypting token: {e}")
        return

    # Now try to call the Instagram API directly
    import httpx

    test_image_url = f"{settings.PUBLIC_BASE_URL}/public/uploads/test.jpg"

    print(f"Attempting to create media container with:")
    print(f"  Account ID: {social_account.account_id}")
    print(f"  Image URL: {test_image_url}")
    print(f"  API Version: {settings.GRAPH_API_VERSION}\n")

    async with httpx.AsyncClient() as client:
        # Test media container creation
        try:
            payload = {
                "image_url": test_image_url,
                "caption": "Debug test",
                "access_token": access_token,
            }

            response = await client.post(
                f"https://graph.instagram.com/{settings.GRAPH_API_VERSION}/{social_account.account_id}/media",
                json=payload,
                timeout=10.0,
            )

            print(f"Media Container Response:")
            print(f"  Status: {response.status_code}")
            print(f"  Body: {response.text[:500]}\n")

            if response.status_code >= 400:
                print("ERROR: Instagram API returned an error")
                try:
                    error_data = response.json()
                    print(f"  Error details: {error_data}")
                except:
                    pass
            else:
                data = response.json()
                print(f"  Success: {data}\n")

        except Exception as e:
            print(f"EXCEPTION during API call: {type(e).__name__}")
            print(f"  str(e): '{str(e)}'")
            print(f"  repr(e): {repr(e)}\n")

asyncio.run(test_flow())
