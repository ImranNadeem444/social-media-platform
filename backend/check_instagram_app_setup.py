"""
Check what the Instagram app is configured for.
"""
import asyncio
import httpx
from app.services.encryption import decrypt_token
from app.db.database import SessionLocal
from app.models.social_account import SocialAccount
from sqlalchemy import select
from app.core.config import settings
import json

db = SessionLocal()
social_account = db.scalar(
    select(SocialAccount).where(SocialAccount.platform == "instagram").limit(1)
)

access_token = decrypt_token(social_account.access_token_encrypted)

print("=" * 80)
print("INSTAGRAM APP & OAUTH SETUP VERIFICATION")
print("=" * 80)

async def check():
    async with httpx.AsyncClient(timeout=20.0) as client:
        # Check what the app itself knows about our configuration
        print(f"\n1. Check app info:")

        # Get app details
        app_id = settings.INSTAGRAM_APP_ID

        # Try to understand what type of login this is
        print(f"\n   Test 1: Check if this is OAuth token or access token")
        print(f"   OAuth Scopes requested in authorization: instagram_business_basic,instagram_business_content_publish")
        print(f"   Scope 'instagram_business_basic' = Business Account Basic Access")
        print(f"   Scope 'instagram_business_content_publish' = Can publish content to Business Account")

        # Check token type via debug endpoint (if available)
        print(f"\n   Test 2: Attempt to debug token")
        response = await client.get(
            f"https://graph.instagram.com/debug_token",
            params={
                "input_token": access_token,
                "access_token": access_token
            }
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        if "data" in data:
            print(f"   Token info: {json.dumps(data['data'], indent=6)}")
        else:
            print(f"   Response: {json.dumps(data, indent=6)}")

        # Try to get the user who authorized
        print(f"\n   Test 3: Get current OAuth user")
        response = await client.get(
            f"https://graph.instagram.com/me",
            params={
                "fields": "id,username,name,account_type",
                "access_token": access_token
            }
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=6)}")

        # Check if there's a way to see connected accounts
        print(f"\n   Test 4: Check if there's a Business Account connected")
        response = await client.get(
            f"https://graph.instagram.com/me",
            params={
                "fields": "id,business_account",
                "access_token": access_token
            }
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        if "error" in data:
            print(f"   Error: {data['error']['message']}")
        else:
            print(f"   Response: {json.dumps(data, indent=6)}")

asyncio.run(check())

print(f"\n2. WHAT WE KNOW:")
print(f"   - OAuth scopes request 'instagram_business_content_publish'")
print(f"   - This means the app expects a Business Account")
print(f"   - The token was obtained with these scopes")
print(f"   - BUT the account ID returned is Personal/Creator only (not Business)")
print(f"\n3. POSSIBLE SCENARIOS:")
print(f"   Scenario A: User has both Personal AND Business Account")
print(f"     - Connected the PERSONAL account instead of Business")
print(f"     - OAuth still succeeded (Instagram allows Personal login)")
print(f"     - But /media endpoint requires Business Account")
print(f"\n   Scenario B: Account was converted, but token is stale")
print(f"     - Account testi_nsta05 was changed to Business")
print(f"     - Token was obtained before the change")
print(f"     - Token still shows as Personal account")
print(f"     - Solution: Reconnect (re-authorize) the account")
print(f"\n   Scenario C: Instagram Login was set up for Personal accounts")
print(f"     - The app allows Personal account OAuth")
print(f"     - But /media endpoint requires Business Account")
print(f"     - This is a configuration mismatch")

print("\n" + "=" * 80)
