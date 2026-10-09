"""
Verify the actual Instagram account type and required setup.
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

print("=" * 80)
print("INSTAGRAM ACCOUNT VERIFICATION")
print("=" * 80)

print(f"\n1. DATABASE RECORD:")
print(f"   Account ID: {social_account.account_id}")
print(f"   Account Name: {social_account.account_name}")
print(f"   User ID: {social_account.user_id}")
print(f"   Created: {social_account.created_at}")

access_token = decrypt_token(social_account.access_token_encrypted)
account_id = social_account.account_id

print(f"\n2. CHECKING ACCOUNT FIELDS VIA GRAPH API:")

async def verify():
    async with httpx.AsyncClient(timeout=20.0) as client:
        # Check basic account info
        print(f"\n   Test 1: Basic info (id, username)")
        response = await client.get(
            f"https://graph.instagram.com/{account_id}",
            params={"access_token": access_token}
        )
        data = response.json()
        print(f"   Status: {response.status_code}")
        print(f"   Data: {json.dumps(data, indent=6)}")

        # Check for business fields
        print(f"\n   Test 2: Business-related fields")
        response = await client.get(
            f"https://graph.instagram.com/{account_id}",
            params={
                "fields": "name,username,biography,profile_picture_url,website,ig_metadata",
                "access_token": access_token
            }
        )
        data = response.json()
        print(f"   Status: {response.status_code}")
        if "error" in data:
            print(f"   Error: {data['error']['message']}")
        else:
            print(f"   Data: {json.dumps(data, indent=6)}")

        # Check if we can access user fields (Personal account can)
        print(f"\n   Test 3: User fields (personal account only)")
        response = await client.get(
            f"https://graph.instagram.com/{account_id}",
            params={
                "fields": "id,username",
                "access_token": access_token
            }
        )
        print(f"   Status: {response.status_code}")

        # Check token introspection - what scopes does this token have?
        print(f"\n   Test 4: Token permissions/scopes")
        response = await client.get(
            f"https://graph.instagram.com/me/permissions",
            params={"access_token": access_token}
        )
        data = response.json()
        print(f"   Status: {response.status_code}")
        if "data" in data:
            perms = data.get("data", [])
            print(f"   Permissions found: {len(perms)}")
            for perm in perms:
                print(f"     - {perm.get('permission', '?')}: {perm.get('status', '?')}")
        else:
            print(f"   Data: {json.dumps(data, indent=6)}")

        # Check if business endpoints work
        print(f"\n   Test 5: Business account endpoints")
        response = await client.get(
            f"https://graph.instagram.com/{account_id}",
            params={
                "fields": "business_account_id,catalog_id,label_ids",
                "access_token": access_token
            }
        )
        data = response.json()
        print(f"   Status: {response.status_code}")
        if "error" in data:
            print(f"   Error: {data['error']['message']} (Code: {data['error'].get('code')})")
        else:
            print(f"   Data: {json.dumps(data, indent=6)}")

        # Check current login session
        print(f"\n   Test 6: Current user (me endpoint)")
        response = await client.get(
            f"https://graph.instagram.com/me",
            params={"access_token": access_token}
        )
        data = response.json()
        print(f"   Status: {response.status_code}")
        if "error" in data:
            print(f"   Error: {data['error']['message']}")
        else:
            print(f"   Data: {json.dumps(data, indent=6)}")

asyncio.run(verify())

print(f"\n3. INSTAGRAM APP CONFIGURATION (from .env):")
print(f"   App ID: {settings.INSTAGRAM_APP_ID}")
print(f"   Redirect URI: {settings.INSTAGRAM_REDIRECT_URI}")
print(f"   Scope in OAuth: instagram_business_basic,instagram_business_content_publish")

print(f"\n4. ANALYSIS:")
print(f"   - The OAuth scopes include 'instagram_business_content_publish'")
print(f"   - This scope is specifically for Business accounts")
print(f"   - If the account cannot publish, it may indicate:")
print(f"     a) The token doesn't have the required scope")
print(f"     b) The account isn't properly set up as Business")
print(f"     c) The account doesn't meet Instagram's Business requirements")
print(f"     d) There's a mismatch between account type and expected account type")

print("\n" + "=" * 80)
