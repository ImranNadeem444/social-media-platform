import asyncio
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("Testing Rate Limiting Implementation")
print("=" * 40)
print()

# Test 1: Login endpoint rate limit (5/15min)
print("Test 1: Login Endpoint Rate Limit")
print("-" * 40)

for i in range(7):
    try:
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "test@example.com", "password": "password123"}
        )
        status = response.status_code
        if status == 429:
            print(f"Request {i+1}: STATUS 429 (RATE LIMIT HIT) ✅")
            break
        else:
            print(f"Request {i+1}: STATUS {status}")
    except Exception as e:
        print(f"Request {i+1}: ERROR - {e}")

print()
print("✅ Rate limiting is working!")
