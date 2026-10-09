"""
Test different API variations to isolate the issue.
"""
import asyncio
import httpx
import json
from app.services.encryption import decrypt_token
from app.db.database import SessionLocal
from app.models.social_account import SocialAccount
from sqlalchemy import select

MINIMAL_JPEG = bytes.fromhex(
    'ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432'
    'ffc000110800010001030122000211010311010000ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9fa'
    'ffda000c03010002110311003f00f2ffd9'
)

from app.services.file_storage import save_upload, generate_public_url

# Save test image
filename = save_upload(MINIMAL_JPEG, "test_variants.jpg")
public_url = generate_public_url(filename)

print(f"Test image URL: {public_url}\n")

db = SessionLocal()
social_account = db.scalar(
    select(SocialAccount).where(SocialAccount.platform == "instagram").limit(1)
)

access_token = decrypt_token(social_account.access_token_encrypted)
account_id = social_account.account_id

print(f"Account: {social_account.account_name} (ID: {account_id})\n")

async def run_tests():
    async with httpx.AsyncClient(timeout=20.0) as client:
        # Test 1: With caption
        print(f"\n{'='*70}")
        print(f"TEST 1: With caption")
        print(f"{'='*70}")
        payload = {
            "image_url": public_url,
            "caption": "Test caption",
            "access_token": access_token,
        }
        response = await client.post(
            f"https://graph.instagram.com/v26.0/{account_id}/media",
            json=payload,
        )
        print(f"Status: {response.status_code}")
        print(f"Body: {json.dumps(response.json(), indent=2)}")

        # Test 2: Without caption
        print(f"\n{'='*70}")
        print(f"TEST 2: Without caption parameter")
        print(f"{'='*70}")
        payload = {
            "image_url": public_url,
            "access_token": access_token,
        }
        response = await client.post(
            f"https://graph.instagram.com/v26.0/{account_id}/media",
            json=payload,
        )
        print(f"Status: {response.status_code}")
        print(f"Body: {json.dumps(response.json(), indent=2)}")

        # Test 3: Check if this is a Business account
        print(f"\n{'='*70}")
        print(f"TEST 3: Get account info")
        print(f"{'='*70}")
        response = await client.get(
            f"https://graph.instagram.com/{account_id}",
            params={
                "fields": "id,username,biography,profile_picture_url,website",
                "access_token": access_token,
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Body: {json.dumps(response.json(), indent=2)}")

asyncio.run(run_tests())

# Cleanup
from pathlib import Path
file_path = Path(f"D:\\social-media-platform\\backend\\public\\uploads\\{filename}")
file_path.unlink(missing_ok=True)
print(f"\nTest file cleaned up")
