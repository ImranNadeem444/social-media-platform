from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings


limiter = Limiter(key_func=get_remote_address)


def get_login_limit() -> str:
    return settings.RATE_LIMIT_LOGIN


def get_register_limit() -> str:
    return settings.RATE_LIMIT_REGISTER


def get_oauth_limit() -> str:
    return settings.RATE_LIMIT_OAUTH


def get_facebook_pages_limit() -> str:
    return settings.RATE_LIMIT_FACEBOOK_PAGES


def get_upload_limit() -> str:
    return settings.RATE_LIMIT_UPLOAD
