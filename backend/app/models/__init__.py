from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.user import User
from app.models.social_account import SocialAccount
from app.models.oauth_state import OAuthState
from app.models.post import Post
from app.models.post_target import PostTarget
from app.models.facebook_oauth_session import FacebookOAuthSession
from app.models.audit_log import AuditLog
