import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.facebook_oauth_session import FacebookOAuthSession
from app.services.encryption import encrypt_token


# ============================================================
# OAuth STATE
# ============================================================

def generate_random_state() -> str:
    """
    Generate a cryptographically secure OAuth state value.

    This is used to protect the OAuth callback against CSRF attacks.
    """
    return secrets.token_hex(32)


# ============================================================
# SELECTION TOKEN
# ============================================================

def generate_selection_token() -> tuple[str, str]:
    """
    Generate a temporary token used by the frontend when selecting
    Facebook Pages.

    Returns:
        raw token
        SHA-256 hash of token
    """
    token = secrets.token_hex(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    return token, token_hash


# ============================================================
# FACEBOOK AUTHORIZATION URL
# ============================================================

def build_authorization_url(state: str) -> str:
    """
    Build the Facebook Login for Business authorization URL.

    The Facebook Login for Business configuration controls the
    permissions requested from the user.

    We therefore pass config_id instead of manually passing scope.
    """

    params = {
        "client_id": settings.FACEBOOK_APP_ID,
        "config_id": settings.FACEBOOK_CONFIG_ID,
        "redirect_uri": settings.FACEBOOK_REDIRECT_URI,
        "response_type": "code",
        "state": state,
    }

    query_string = urlencode(params)

    graph_version = settings.GRAPH_API_VERSION.replace("v", "")

    return (
        f"https://www.facebook.com/v{graph_version}/dialog/oauth?"
        f"{query_string}"
    )


# ============================================================
# EXCHANGE OAUTH CODE FOR USER ACCESS TOKEN
# ============================================================

async def exchange_code_for_user_token(code: str) -> dict:
    """
    Exchange the temporary OAuth authorization code for a
    Facebook User Access Token.
    """

    url = (
        f"https://graph.facebook.com/"
        f"{settings.GRAPH_API_VERSION}/oauth/access_token"
    )

    payload = {
        "client_id": settings.FACEBOOK_APP_ID,
        "client_secret": settings.FACEBOOK_APP_SECRET,
        "redirect_uri": settings.FACEBOOK_REDIRECT_URI,
        "code": code,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:

        try:
            response = await client.post(
                url,
                data=payload,
            )

        except httpx.RequestError as exc:
            print(
                "[FACEBOOK_OAUTH_ERROR] "
                f"Token exchange request failed: {type(exc).__name__}"
            )
            raise

        # ----------------------------------------------------
        # Facebook API error handling
        # ----------------------------------------------------

        if response.status_code >= 400:

            try:
                error_data = response.json()

            except json.JSONDecodeError:
                error_data = {}

            error = error_data.get("error")

            if error:
                error_message = error.get(
                    "message",
                    "Unknown Facebook error",
                )

                error_code = error.get(
                    "code",
                    "?",
                )

                error_type = error.get(
                    "type",
                    "?",
                )

                print(
                    "[FACEBOOK_OAUTH_ERROR] "
                    f"/oauth/access_token: "
                    f"{error_type} "
                    f"(code {error_code}): "
                    f"{error_message}"
                )

                raise ValueError(
                    f"Facebook token exchange failed: "
                    f"{error_message}"
                )

        response.raise_for_status()

        return response.json()


# ============================================================
# FETCH FACEBOOK PAGES
# ============================================================

async def fetch_user_pages(access_token: str) -> dict:
    """
    Fetch Facebook Pages that the authorized Facebook user
    can manage.

    The User Access Token is used to query /me/accounts.

    Facebook returns Page Access Tokens for the discovered Pages.
    """

    url = (
        f"https://graph.facebook.com/"
        f"{settings.GRAPH_API_VERSION}/me/accounts"
    )

    params = {
        "fields": "id,name,access_token,tasks",
        "access_token": access_token,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:

        try:
            response = await client.get(
                url,
                params=params,
            )

        except httpx.RequestError as exc:
            print(
                "[FACEBOOK_PAGE_DISCOVERY_ERROR] "
                f"Request failed: {type(exc).__name__}"
            )
            raise

        # ----------------------------------------------------
        # Facebook API error handling
        # ----------------------------------------------------

        if response.status_code >= 400:

            try:
                error_data = response.json()

            except json.JSONDecodeError:
                error_data = {}

            error = error_data.get("error")

            if error:
                error_message = error.get(
                    "message",
                    "Unknown Facebook error",
                )

                error_code = error.get(
                    "code",
                    "?",
                )

                error_type = error.get(
                    "type",
                    "?",
                )

                print(
                    "[FACEBOOK_PAGE_DISCOVERY_ERROR] "
                    f"GET /me/accounts: "
                    f"{error_type} "
                    f"(code {error_code}): "
                    f"{error_message}"
                )

                raise ValueError(
                    f"Failed to fetch pages: "
                    f"{error_message}"
                )

        response.raise_for_status()

        data = response.json()

        # ----------------------------------------------------
        # Helpful diagnostic
        # ----------------------------------------------------

        pages = data.get("data", [])

        print(
            "[FACEBOOK_PAGE_DISCOVERY] "
            f"Found {len(pages)} page(s)"
        )

        return data


# ============================================================
# CREATE FACEBOOK PAGE SELECTION SESSION
# ============================================================

def create_facebook_selection_session(
    user_id: int,
    page_candidates: list[dict],
    user_access_token: str,
    db: Session,
) -> tuple[str, FacebookOAuthSession]:
    """
    Create a temporary server-side session used while the user
    chooses which Facebook Pages to connect.

    The actual User Access Token is encrypted before storage.

    Only a hash of the selection token is stored.
    """

    selection_token, token_hash = generate_selection_token()

    encrypted_token = encrypt_token(
        user_access_token
    )

    session = FacebookOAuthSession(
        user_id=user_id,
        selection_token_hash=token_hash,
        page_candidates=json.dumps(page_candidates),
        user_access_token_encrypted=encrypted_token,
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        ),
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return selection_token, session


# ============================================================
# VALIDATE FACEBOOK PAGE SELECTION SESSION
# ============================================================

def validate_facebook_selection_session(
    selection_token: str,
    user_id: int,
    db: Session,
) -> FacebookOAuthSession:
    """
    Validate the temporary Page-selection session.

    Requirements:
    - token must exist
    - token must belong to current user
    - token must not be expired
    - token must not already be used
    """

    token_hash = hashlib.sha256(
        selection_token.encode("utf-8")
    ).hexdigest()

    session = db.scalar(
        select(FacebookOAuthSession)
        .where(
            FacebookOAuthSession.selection_token_hash
            == token_hash
        )
        .where(
            FacebookOAuthSession.user_id
            == user_id
        )
    )

    if not session:
        raise ValueError(
            "Invalid selection token"
        )

    if session.expires_at < datetime.now(timezone.utc):
        raise ValueError(
            "Selection session expired"
        )

    if session.used_at is not None:
        raise ValueError(
            "Selection session already used"
        )

    return session


# ============================================================
# MARK SELECTION SESSION AS USED
# ============================================================

def mark_selection_session_used(
    session: FacebookOAuthSession,
    db: Session,
) -> None:
    """
    Mark the Page-selection session as consumed.
    """

    session.used_at = datetime.now(timezone.utc)

    db.commit()


# ============================================================
# GET PAGE CANDIDATES
# ============================================================

def get_page_candidates(
    session: FacebookOAuthSession,
) -> list[dict]:
    """
    Deserialize the stored Facebook Page candidates.
    """

    try:
        candidates = json.loads(
            session.page_candidates
        )

    except (json.JSONDecodeError, TypeError):
        raise ValueError(
            "Invalid stored Facebook Page candidates"
        )

    if not isinstance(candidates, list):
        raise ValueError(
            "Invalid Facebook Page candidates"
        )

    return candidates