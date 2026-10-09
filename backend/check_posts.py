from sqlalchemy import select
from app.db.database import SessionLocal
from app.models.post import Post

db = SessionLocal()

posts = db.scalars(select(Post).order_by(Post.created_at.desc()).limit(5)).all()

print("Recent Posts:")
for post in posts:
    print(f"\nID: {post.id}")
    print(f"  Status: {post.status}")
    print(f"  Instagram Media ID: {post.instagram_media_id}")
    print(f"  Error Message: {post.error_message}")
    print(f"  Image Path: {post.image_path}")
    print(f"  Caption: {post.caption}")
    print(f"  Created: {post.created_at}")
