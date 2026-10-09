import httpx
import asyncio
from pathlib import Path
from app.core.config import settings

async def check_image():
    # First check locally
    print("Checking uploaded image files:\n")

    upload_dir = Path(__file__).parent / "public" / "uploads"
    if upload_dir.exists():
        files = list(upload_dir.glob("*.jpg")) + list(upload_dir.glob("*.jpeg")) + list(upload_dir.glob("*.png"))
        for f in files[:2]:  # Check first 2
            size = f.stat().st_size
            print(f"File: {f.name}")
            print(f"  Size: {size} bytes")
            print(f"  Exists: True\n")
    else:
        print("Upload directory does not exist")
        return

    # Now check via HTTP
    print("\nChecking image served via HTTP:\n")

    if not files:
        print("No uploaded images found")
        return

    test_file = files[0].name
    test_url = f"{settings.PUBLIC_BASE_URL}/public/uploads/{test_file}"

    print(f"Test URL: {test_url}\n")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(test_url, follow_redirects=True, timeout=10.0)

            print(f"Status: {response.status_code}")
            print(f"Headers:")
            for key, value in response.headers.items():
                if key.lower() in ['content-type', 'content-length', 'server', 'date']:
                    print(f"  {key}: {value}")

            print(f"\nBody size: {len(response.content)} bytes")
            print(f"First 20 bytes: {response.content[:20]}")

            # Check if it's valid JPEG/PNG
            if response.content[:3] == b'\xff\xd8\xff':
                print("✓ Valid JPEG header")
            elif response.content[:8] == b'\x89PNG\r\n\x1a\n':
                print("✓ Valid PNG header")
            else:
                print("✗ NOT a valid image file!")
                print(f"First 50 chars: {response.text[:50]}")

        except Exception as e:
            print(f"ERROR: {e}")

asyncio.run(check_image())
