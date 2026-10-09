import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.oauth_state import OAuthState
from app.services.encryption import encrypt_token


def generate_random_state() -> str:
    return secrets.token_hex(32)


def build_authorization_url(state: str) -> str:
    params = {
        "client_id": settings.INSTAGRAM_APP_ID,
        "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
        "scope": "instagram_business_basic,instagram_business_content_publish",
        "response_type": "code",
        "state": state,
        "enable_fb_login": "0",
    }

    query_string = urlencode(params)

    return f"https://www.instagram.com/oauth/authorize?{query_string}"


async def exchange_code_for_short_lived_token(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.instagram.com/oauth/access_token",
            data={
                "client_id": settings.INSTAGRAM_APP_ID,
                "client_secret": settings.INSTAGRAM_APP_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
                "code": code,
            },
        )
        response.raise_for_status()
        return response.json()


async def exchange_short_lived_for_long_lived(
    short_lived_token: str,
) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://graph.instagram.com/access_token",
            params={
                "grant_type": "ig_exchange_token",
                "client_secret": settings.INSTAGRAM_APP_SECRET,
                "access_token": short_lived_token,
            },
        )
        response.raise_for_status()
        return response.json()


async def fetch_instagram_account_identity(
    long_lived_token: str,
    user_id: str,
) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://graph.instagram.com/{user_id}",
            params={
                "fields": "id,username",
                "access_token": long_lived_token,
            },
        )
        response.raise_for_status()
        return response.json()


def create_oauth_state(
    user_id: int,
    state: str,
    db: Session,
) -> OAuthState:
    oauth_state = OAuthState(
        user_id=user_id,
        state=state,
        platform="instagram",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    db.add(oauth_state)
    db.commit()

    return oauth_state


def validate_oauth_state(state: str, db: Session) -> OAuthState:
    oauth_state = db.scalar(
        select(OAuthState)
        .where(OAuthState.state == state)
        .where(OAuthState.platform == "instagram")
    )

    if not oauth_state:
        raise ValueError("Invalid state")

    if oauth_state.expires_at < datetime.now(timezone.utc):
        raise ValueError("State expired")

    if oauth_state.used_at is not None:
        raise ValueError("State already used")

    return oauth_state


def consume_oauth_state(
    oauth_state: OAuthState,
    db: Session,
) -> None:
    oauth_state.used_at = datetime.now(timezone.utc)
    db.commit()