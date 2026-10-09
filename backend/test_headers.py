from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("Testing Security Headers")
print("=" * 50)
print()

response = client.get("/health")

print(f"Status Code: {response.status_code}")
print()

required_headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-XSS-Protection": "1; mode=block"
}

print("Security Headers:")
print("-" * 50)

all_present = True
for header, expected_value in required_headers.items():
    actual_value = response.headers.get(header)
    if actual_value == expected_value:
        print(f"✅ {header}: {actual_value}")
    else:
        print(f"❌ {header}: {actual_value} (expected: {expected_value})")
        all_present = False

print()
if all_present:
    print("✅ All security headers present and correct!")
else:
    print("⚠️ Some headers missing or incorrect")
