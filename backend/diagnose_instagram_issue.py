"""
Comprehensive diagnostic test for Instagram 9004 error.
Captures all relevant information during a single upload/publish attempt.
"""
import asyncio
import httpx
from pathlib import Path
import json

# Use a minimal valid JPEG (actual JPEG file with FF D8 FF header)
# This is a 1x1 red pixel JPEG
MINIMAL_JPEG = bytes.fromhex(
    'ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432'
    'ffc000110800010001030122000211010311010000ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9fa'
    'ffda000c03010002110311003f00f2ffd9'
)

test_image_bytes = MINIMAL_JPEG
print(f"Test image size: {len(test_image_bytes)} bytes")
print(f"Test image magic bytes: {test_image_bytes[:4].hex()}")
print(f"Is valid JPEG (FF D8 FF): {test_image_bytes[:3].hex() == 'ffd8ff'}")
print()

# Simulate the upload
print("=" * 80)
print("STEP 1: Simulate file upload through API")
print("=" * 80)

from app.services.file_storage import save_upload, generate_public_url, UPLOAD_DIR
from app.core.config import settings

filename = save_upload(test_image_bytes, "test_image.jpg")
print(f"✓ File saved: {filename}")

file_path = UPLOAD_DIR / filename
print(f"✓ Full path: {file_path}")
print(f"✓ File exists: {file_path.exists()}")
print(f"✓ File size: {file_path.stat().st_size} bytes")

# Check file magic bytes
saved_bytes = file_path.read_bytes()
print(f"✓ Saved file magic bytes: {saved_bytes[:4].hex()}")
print(f"✓ Is valid JPEG: {saved_bytes[:3].hex() == 'ffd8ff'}")

# Generate URL
public_url = generate_public_url(filename)
print(f"✓ Generated URL: {public_url}")
print()

# Test the URL
print("=" * 80)
print("STEP 2: Test HTTP response from /public/uploads/{filename}")
print("=" * 80)

async def test_image_url():
    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
        try:
            response = await client.head(public_url)
            print(f"✓ HEAD request status: {response.status_code}")
            print(f"✓ Content-Type: {response.headers.get('content-type', 'NOT SET')}")
            print(f"✓ Content-Length: {response.headers.get('content-length', 'NOT SET')}")
            print(f"✓ Content-Disposition: {response.headers.get('content-disposition', 'NOT SET')}")
            print(f"✓ Server: {response.headers.get('server', 'NOT SET')}")
            print()

            # Now do a GET to verify body
            response = await client.get(public_url)
            print(f"✓ GET request status: {response.status_code}")
            print(f"✓ GET response size: {len(response.content)} bytes")
            print(f"✓ GET response magic bytes: {response.content[:4].hex()}")
            print(f"✓ GET response is JPEG: {response.content[:3].hex() == 'ffd8ff'}")
            print(f"✓ Matches uploaded file: {response.content == saved_bytes}")

            if response.status_code == 200:
                if response.content[:3].hex() != 'ffd8ff':
                    print(f"\n⚠️  WARNING: Response body is NOT a valid JPEG!")
                    print(f"    First 100 chars: {response.content[:100]}")

        except Exception as e:
            print(f"✗ Error testing URL: {e}")

asyncio.run(test_image_url())
print()

# Test Instagram API call
print("=" * 80)
print("STEP 3: Call Instagram /media endpoint with our URL")
print("=" * 80)

from app.services.encryption import decrypt_token
from app.db.database import SessionLocal
from app.models.social_account import SocialAccount
from sqlalchemy import select

db = SessionLocal()
social_account = db.scalar(
    select(SocialAccount).where(SocialAccount.platform == "instagram").limit(1)
)

if not social_account:
    print("✗ No Instagram account found")
else:
    print(f"✓ Using account: {social_account.account_name}")

    try:
        access_token = decrypt_token(social_account.access_token_encrypted)
        print(f"✓ Token decrypted")
    except Exception as e:
        print(f"✗ Failed to decrypt token: {e}")
        access_token = None

    if access_token:
        async def test_instagram_api():
            async with httpx.AsyncClient(timeout=20.0) as client:
                payload = {
                    "image_url": public_url,
                    "caption": "Diagnostic test from backend",
                    "access_token": access_token,
                }

                print(f"\nCalling: POST /v26.0/{social_account.account_id}/media")
                print(f"Image URL: {public_url}")

                try:
                    response = await client.post(
                        f"https://graph.instagram.com/v26.0/{social_account.account_id}/media",
                        json=payload,
                        timeout=20.0,
                    )

                    print(f"\n✓ HTTP Status: {response.status_code}")
                    print(f"✓ Response size: {len(response.text)} bytes")

                    try:
                        data = response.json()
                        print(f"✓ Response JSON:")
                        print(json.dumps(data, indent=2))
                    except:
                        print(f"✓ Response text: {response.text[:500]}")

                    if response.status_code >= 400:
                        print(f"\n✗ ERROR: Instagram returned {response.status_code}")
                        if 'error' in response.text:
                            error_data = response.json().get('error', {})
                            print(f"  Error code: {error_data.get('code')}")
                            print(f"  Error message: {error_data.get('message')}")
                            print(f"  Error subcode: {error_data.get('error_subcode')}")

                except httpx.TimeoutException:
                    print(f"✗ Request timed out (20s)")
                except Exception as e:
                    print(f"✗ Exception: {type(e).__name__}: {e}")

        asyncio.run(test_instagram_api())

print()
print("=" * 80)
print("STEP 4: Cleanup")
print("=" * 80)

# Clean up
file_path.unlink(missing_ok=True)
print(f"✓ Test file deleted")

print("\n" + "=" * 80)
print("DIAGNOSTICS COMPLETE")
print("=" * 80)
