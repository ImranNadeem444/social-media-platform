"""
Test what exception looks like for a 500 error from Instagram.
"""
import asyncio
import httpx
from app.services.encryption import decrypt_token
from app.db.database import SessionLocal
from app.models.social_account import SocialAccount
from sqlalchemy import select
from app.services.file_storage import save_upload, generate_public_url

MINIMAL_JPEG = bytes.fromhex(
    'ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432'
    'ffc000110800010001030122000211010311010000ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9fa'
    'ffda000c03010002110311003f00f2ffd9'
)

# Setup
filename = save_upload(MINIMAL_JPEG, "test_exception.jpg")
public_url = generate_public_url(filename)

db = SessionLocal()
social_account = db.scalar(
    select(SocialAccount).where(SocialAccount.platform == "instagram").limit(1)
)
access_token = decrypt_token(social_account.access_token_encrypted)

async def test():
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            response = await client.post(
                f"https://graph.instagram.com/v26.0/{social_account.account_id}/media",
                json={
                    "image_url": public_url,
                    "caption": "test",
                    "access_token": access_token,
                }
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print("Caught HTTPStatusError:")
            print(f"  type: {type(e).__name__}")
            print(f"  str(e): '{str(e)}'")
            print(f"  str(e) length: {len(str(e))}")
            print(f"  repr(e): {repr(e)}")
            print(f"  e.response.status_code: {e.response.status_code}")
            print(f"  e.response.text: {e.response.text[:200]}")
            print(f"\nException args:")
            print(f"  e.args: {e.args}")
            print(f"  len(e.args): {len(e.args)}")
            if e.args:
                print(f"  e.args[0]: '{e.args[0]}'")

asyncio.run(test())

# Cleanup
from pathlib import Path
Path(f"D:\\social-media-platform\\backend\\public\\uploads\\{filename}").unlink(missing_ok=True)
