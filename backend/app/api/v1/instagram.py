from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.rate_limiting import limiter
from app.core.security_logger import (
    log_oauth_start,
    log_oauth_success,
    log_oauth_failure,
)
from app.db.database import get_db
from app.models.social_account import SocialAccount
from app.models.user import User
from app.services.encryption import encrypt_token
from app.services.instagram_oauth import (
    build_authorization_url,
    consume_oauth_state,
    create_oauth_state,
    exchange_code_for_short_lived_token,
    exchange_short_lived_for_long_lived,
    fetch_instagram_account_identity,
    generate_random_state,
    validate_oauth_state,
)


router = APIRouter(
    prefix="/social-accounts/instagram",
    tags=["Instagram OAuth"],
)


@router.get("/authorize")
@limiter.limit("3/10min")
def authorize_instagram(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    state = generate_random_state()
    create_oauth_state(current_user.id, state, db)
    authorization_url = build_authorization_url(state)

    log_oauth_start(current_user.id, "instagram", request, db)

    return {"authorization_url": authorization_url}


@router.get("/callback")
@limiter.limit("3/10min")
async def callback_instagram(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    from fastapi.responses import RedirectResponse
    from app.core.config import settings
    from urllib.parse import quote

    try:
        oauth_state = validate_oauth_state(state, db)
    except ValueError as e:
        error_msg = "Invalid or expired authorization state"
        log_oauth_failure(None, "instagram", error_msg, request, db)
        from urllib.parse import quote
        return RedirectResponse(
            url=f"{settings.FRONTEND_BASE_URL}/instagram/error?error={quote(error_msg)}",
            status_code=status.HTTP_302_FOUND,
        )

    user_id = oauth_state.user_id

    try:
        consume_oauth_state(oauth_state, db)
    except Exception:
        error_msg = "Failed to process authorization state"
        log_oauth_failure(user_id, "instagram", error_msg, request, db)
        return RedirectResponse(
            url=f"{settings.FRONTEND_BASE_URL}/instagram/error?error={quote(error_msg)}",
            status_code=status.HTTP_302_FOUND,
        )

    try:
        short_lived_response = await exchange_code_for_short_lived_token(code)
        short_lived_token = short_lived_response["access_token"]
        instagram_user_id = short_lived_response["user_id"]
    except Exception as e:
        error_msg = "Failed to exchange authorization code"
        log_oauth_failure(user_id, "instagram", str(e), request, db)
        return RedirectResponse(
            url=f"{settings.FRONTEND_BASE_URL}/instagram/error?error={quote(error_msg)}",
            status_code=status.HTTP_302_FOUND,
        )

    try:
        long_lived_response = await exchange_short_lived_for_long_lived(
            short_lived_token
        )
        long_lived_token = long_lived_response["access_token"]
        expires_in = long_lived_response.get("expires_in")
    except Exception as e:
        error_msg = "Failed to obtain long-lived token"
        log_oauth_failure(user_id, "instagram", str(e), request, db)
        return RedirectResponse(
            url=f"{settings.FRONTEND_BASE_URL}/instagram/error?error={quote(error_msg)}",
            status_code=status.HTTP_302_FOUND,
        )

    try:
        account_data = await fetch_instagram_account_identity(
            long_lived_token,
            str(instagram_user_id),
        )
        account_id = account_data["id"]
        account_name = account_data.get("username")
    except Exception as e:
        error_msg = "Failed to fetch Instagram account"
        log_oauth_failure(user_id, "instagram", str(e), request, db)
        return RedirectResponse(
            url=f"{settings.FRONTEND_BASE_URL}/instagram/error?error={quote(error_msg)}",
            status_code=status.HTTP_302_FOUND,
        )

    encrypted_token = encrypt_token(long_lived_token)

    from datetime import datetime, timedelta, timezone

    token_expires_at = None
    if expires_in:
        token_expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=expires_in
        )

    existing_account = db.scalar(
        select(SocialAccount)
        .where(SocialAccount.user_id == user_id)
        .where(SocialAccount.platform == "instagram")
        .where(SocialAccount.account_id == account_id)
    )

    if existing_account:
        existing_account.access_token_encrypted = encrypted_token
        existing_account.token_expires_at = token_expires_at
        existing_account.account_name = account_name
    else:
        social_account = SocialAccount(
            user_id=user_id,
            platform="instagram",
            account_id=account_id,
            account_name=account_name,
            access_token_encrypted=encrypted_token,
            token_expires_at=token_expires_at,
        )
        db.add(social_account)

    db.commit()

    log_oauth_success(user_id, "instagram", account_name, request, db)

    return RedirectResponse(
        url=f"{settings.FRONTEND_BASE_URL}/instagram/success?account_name={quote(account_name)}",
        status_code=status.HTTP_302_FOUND,
    )
