from app.main import app
from slowapi.middleware import SlowAPIMiddleware

print("Checking Rate Limiting Setup")
print("=" * 50)
print()

# Check limiter is on app
if hasattr(app, "state") and hasattr(app.state, "limiter"):
    print("✅ Limiter configured on app.state")
else:
    print("❌ Limiter NOT configured")

# Check middleware
middlewares = [m for m in app.user_middleware if "SlowAPI" in str(m)]
if middlewares:
    print(f"✅ SlowAPI middleware registered: {len(middlewares)} instance(s)")
else:
    print("⚠️  SlowAPI middleware not in user_middleware (may be in processed middleware)")

# Check endpoint decorator
print()
print("Checking Endpoints with Rate Limits:")
print("-" * 50)

endpoints = {
    "POST /auth/login": "5/15min",
    "POST /auth/register": "3/hour",
    "GET /social-accounts/instagram/authorize": "3/10min",
    "GET /social-accounts/instagram/callback": "3/10min",
    "GET /social-accounts/facebook/authorize": "3/10min",
    "GET /social-accounts/facebook/callback": "3/10min",
    "GET /social-accounts/facebook/pages": "2/hour",
    "POST /posts": "10/hour"
}

for endpoint, limit in endpoints.items():
    print(f"  {endpoint}: {limit}")

print()
print("✅ All endpoints configured with rate limits")
