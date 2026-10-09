from sqlalchemy import select, text
from app.db.database import SessionLocal, engine
from app.models.post import Post

# Check via ORM
db = SessionLocal()
posts = db.scalars(select(Post).order_by(Post.created_at.desc()).limit(2)).all()

print("Via SQLAlchemy ORM:")
for post in posts:
    print(f"\nID: {post.id}")
    print(f"  error_message value: {repr(post.error_message)}")
    print(f"  error_message is None: {post.error_message is None}")
    print(f"  error_message == '': {post.error_message == ''}")
    print(f"  len(error_message): {len(post.error_message) if post.error_message else 'N/A'}")

# Check via raw SQL
print("\n\n--- Raw SQL Query ---")
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT id, status, error_message FROM posts ORDER BY created_at DESC LIMIT 2")
    )
    for row in result:
        print(f"ID: {row[0]}, Status: {row[1]}, Error: {repr(row[2])}")
