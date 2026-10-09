"""
Check what's needed for a Business account to publish via /media endpoint.
"""
import asyncio
import httpx
from app.services.encryption import decrypt_token
from app.db.database import SessionLocal
from app.models.social_account import SocialAccount
from sqlalchemy import select
import json

db = SessionLocal()
social_account = db.scalar(
    select(SocialAccount).where(SocialAccount.platform == "instagram").limit(1)
)

access_token = decrypt_token(social_account.access_token_encrypted)
account_id = social_account.account_id

print("=" * 80)
print("BUSINESS ACCOUNT SETUP REQUIREMENTS CHECK")
print("=" * 80)

print(f"\nAccount: {social_account.account_name} (ID: {account_id})")
print(f"Type: BUSINESS (confirmed)")

async def check_requirements():
    async with httpx.AsyncClient(timeout=20.0) as client:

        # Check 1: Does account have required capabilities?
        print(f"\n1. CHECK: Account capabilities")
        response = await client.get(
            f"https://graph.instagram.com/{account_id}",
            params={
                "fields": "id,username,name,biography,website,profile_picture_url",
                "access_token": access_token
            }
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Fields available: {list(data.keys())}")
        print(f"   Data: {json.dumps(data, indent=6)}")

        # Check 2: What about catalog or shop setup?
        print(f"\n2. CHECK: Shop/Commerce setup")
        response = await client.get(
            f"https://graph.instagram.com/{account_id}",
            params={
                "fields": "shopping_settings,catalog_id",
                "access_token": access_token
            }
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        if "error" in data:
            print(f"   Error: {data['error']['message']}")
        else:
            print(f"   Data: {json.dumps(data, indent=6)}")

        # Check 3: Is there a linked Facebook page or business?
        print(f"\n3. CHECK: Connected Pages/Business")
        response = await client.get(
            f"https://graph.instagram.com/{account_id}/pages",
            params={"access_token": access_token}
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        if "error" in data:
            print(f"   Error: {data['error']['message']}")
        else:
            print(f"   Data: {json.dumps(data, indent=6)}")

        # Check 4: Try /media with different image URL formats
        print(f"\n4. CHECK: /media endpoint requirements")

        # Try with a publicly hosted image
        print(f"\n   Test A: /media with https://scontent.instagram.com/ image")
        response = await client.post(
            f"https://graph.instagram.com/v26.0/{account_id}/media",
            json={
                "image_url": "https://www.instagram.com/static/images/web/mobile_nav_type_logo.png/735145cfe0a4.png",
                "caption": "Test from public Instagram CDN",
                "access_token": access_token,
            }
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=6)}")

        # Check 5: Are there any prerequisites we're missing?
        print(f"\n   Test B: /media with base64 data URL")
        # Create a minimal base64 JPEG
        base64_jpeg = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="
        response = await client.post(
            f"https://graph.instagram.com/v26.0/{account_id}/media",
            json={
                "image_url": base64_jpeg,
                "caption": "Test with base64",
                "access_token": access_token,
            }
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=6)}")

asyncio.run(check_requirements())

print(f"\n" + "=" * 80)
print(f"DIAGNOSIS:")
print(f"If /media still returns 500 code 1, the issue is likely:")
print(f"  1. No connected Facebook Page (Business accounts need this)")
print(f"  2. Business account not fully set up/verified")
print(f"  3. Instagram API backend issue for this specific account")
print(f"  4. Account restrictions or compliance issues")
print(f"=" * 80)
