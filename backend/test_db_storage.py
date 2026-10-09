"""
Test if there's a database issue storing multiline exception messages.
"""
from app.db.database import SessionLocal
from app.models.post import Post
from app.models.user import User
from app.models.social_account import SocialAccount
from sqlalchemy import select

# Get test data
db = SessionLocal()
user = db.scalar(select(User).limit(1))
social_account = db.scalar(
    select(SocialAccount).where(SocialAccount.platform == "instagram").limit(1)
)

# Test 1: Store multiline message (simulating HTTPStatusError str())
print("Test 1: Storing multiline exception message")

multiline_msg = """Server error '500 Internal Server Error' for url 'https://graph.instagram.com/v26.0/28628745500110110/media'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500"""

post1 = Post(
    user_id=user.id,
    social_account_id=social_account.id,
    platform="instagram",
    caption="Test",
    image_path="test1.jpg",
    status="failed",
    error_message=multiline_msg,
)

db.add(post1)
db.commit()
db.refresh(post1)

print(f"Stored message: '{multiline_msg}'")
print(f"Retrieved from DB: '{post1.error_message}'")
print(f"Match: {post1.error_message == multiline_msg}")
print(f"Retrieved length: {len(post1.error_message)}")
print()

# Test 2: Store single-line message
print("Test 2: Storing single-line message")

single_line_msg = "Server error '500 Internal Server Error' for url 'https://...'"

post2 = Post(
    user_id=user.id,
    social_account_id=social_account.id,
    platform="instagram",
    caption="Test",
    image_path="test2.jpg",
    status="failed",
    error_message=single_line_msg,
)

db.add(post2)
db.commit()
db.refresh(post2)

print(f"Stored message: '{single_line_msg}'")
print(f"Retrieved from DB: '{post2.error_message}'")
print(f"Match: {post2.error_message == single_line_msg}")
print()

# Test 3: Store empty message
print("Test 3: Storing empty string")

post3 = Post(
    user_id=user.id,
    social_account_id=social_account.id,
    platform="instagram",
    caption="Test",
    image_path="test3.jpg",
    status="failed",
    error_message="",
)

db.add(post3)
db.commit()
db.refresh(post3)

print(f"Stored message: ''")
print(f"Retrieved from DB: '{post3.error_message}'")
print(f"Is empty: {post3.error_message == ''}")
print(f"Is None: {post3.error_message is None}")

# Cleanup
for post in [post1, post2, post3]:
    db.delete(post)
db.commit()

print("\nTest posts cleaned up")
