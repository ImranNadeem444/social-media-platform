from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.rate_limiting import limiter
from app.core.security_logger import (
    log_oauth_start,
    log_oauth_success,
    log_oauth_failure,
)
from app.db.database import get_db
from app.models.facebook_oauth_session import FacebookOAuthSession
from app.models.oauth_state import OAuthState
from app.models.social_account import SocialAccount
from app.models.user import User
from app.services.encryption import encrypt_token
from app.services.facebook_oauth import (
    build_authorization_url,
    create_facebook_selection_session,
    exchange_code_for_user_token,
    fetch_user_pages,
    generate_random_state,
    generate_selection_token,
    get_page_candidates,
    mark_selection_session_used,
    validate_facebook_selection_session,
)


router = APIRouter(
    prefix="/social-accounts/facebook",
    tags=["Facebook OAuth"],
)


@router.get("/authorize")
@limiter.limit("3/10min")
def authorize_facebook(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    state = generate_random_state()

    oauth_state = OAuthState(
        user_id=current_user.id,
        state=state,
        platform="facebook",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    db.add(oauth_state)
    db.commit()

    authorization_url = build_authorization_url(state)

    log_oauth_start(current_user.id, "facebook", request, db)

    return {
        "authorization_url": authorization_url
    }


@router.get("/callback")
@limiter.limit("3/10min")
async def callback_facebook(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    from urllib.parse import quote

    # ---------------------------------------------------------
    # 1. Validate OAuth state
    # ---------------------------------------------------------
    try:
        oauth_state = db.scalar(
            select(OAuthState)
            .where(OAuthState.state == state)
            .where(OAuthState.platform == "facebook")
        )

        if not oauth_state:
            raise ValueError("Invalid state")

        if oauth_state.expires_at < datetime.now(timezone.utc):
            raise ValueError("State expired")

        if oauth_state.used_at is not None:
            raise ValueError("State already used")

    except ValueError as e:
        error_msg = str(e)
        print(
            f"[FACEBOOK_CALLBACK_ERROR] "
            f"OAuth state validation failed: {error_msg}"
        )

        log_oauth_failure(None, "facebook", error_msg, request, db)

        return RedirectResponse(
            url=f"{settings.FRONTEND_BASE_URL}/facebook/error?error={quote(error_msg)}",
            status_code=status.HTTP_302_FOUND,
        )

    user_id = oauth_state.user_id

    # ---------------------------------------------------------
    # 2. Exchange Facebook authorization code for user token
    # ---------------------------------------------------------
    try:
        token_response = await exchange_code_for_user_token(code)

        user_access_token = token_response.get("access_token")

        if not user_access_token:
            raise ValueError("No access token in response")

    except Exception as e:
        error_msg = "Failed to exchange authorization code"
        print(
            f"[FACEBOOK_CALLBACK_ERROR] "
            f"Token exchange failed: {str(e)}"
        )

        log_oauth_failure(user_id, "facebook", str(e), request, db)

        return RedirectResponse(
            url=f"{settings.FRONTEND_BASE_URL}/facebook/error?error={quote(error_msg)}",
            status_code=status.HTTP_302_FOUND,
        )

    # ---------------------------------------------------------
    # 3. Consume OAuth state
    # ---------------------------------------------------------
    try:
        oauth_state.used_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        print(
            f"[FACEBOOK_CALLBACK_ERROR] "
            f"Failed to consume OAuth state: {str(e)}"
        )

        return RedirectResponse(
            url=(
                f"{settings.FRONTEND_BASE_URL}"
                f"/accounts"
                f"?error=Authorization+processing+failed"
            ),
            status_code=status.HTTP_302_FOUND,
        )

    # ---------------------------------------------------------
    # 4. Discover Facebook Pages
    # ---------------------------------------------------------
    try:
        pages_response = await fetch_user_pages(user_access_token)

        page_candidates = pages_response.get("data", [])

        if not page_candidates:
            raise ValueError(
                "No pages available for this Facebook account"
            )

        print(
            f"[FACEBOOK_PAGE_DISCOVERY] "
            f"Found {len(page_candidates)} page(s)"
        )

    except Exception as e:
        error_msg = "Failed to fetch Facebook pages"
        print(
            f"[FACEBOOK_CALLBACK_ERROR] "
            f"Page discovery failed: {str(e)}"
        )

        log_oauth_failure(user_id, "facebook", str(e), request, db)

        return RedirectResponse(
            url=f"{settings.FRONTEND_BASE_URL}/facebook/error?error={quote(error_msg)}",
            status_code=status.HTTP_302_FOUND,
        )

    # ---------------------------------------------------------
    # 5. Create secure page-selection session
    # ---------------------------------------------------------
    try:
        selection_token, _ = create_facebook_selection_session(
            user_id=user_id,
            page_candidates=page_candidates,
            user_access_token=user_access_token,
            db=db,
        )

    except Exception as e:
        error_msg = "Failed to create selection session"
        print(
            f"[FACEBOOK_CALLBACK_ERROR] "
            f"Selection session creation failed: {str(e)}"
        )

        log_oauth_failure(user_id, "facebook", str(e), request, db)

        return RedirectResponse(
            url=f"{settings.FRONTEND_BASE_URL}/facebook/error?error={quote(error_msg)}",
            status_code=status.HTTP_302_FOUND,
        )

    # ---------------------------------------------------------
    # 6. Redirect to FRONTEND page selector
    # ---------------------------------------------------------
    return RedirectResponse(
        url=(
            f"{settings.FRONTEND_BASE_URL}"
            f"/facebook/select-pages"
            f"?selection_token={selection_token}"
        ),
        status_code=status.HTTP_302_FOUND,
    )


@router.get("/pages")
@limiter.limit("2/hour")
def get_facebook_pages(
    request: Request,
    selection_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        session = validate_facebook_selection_session(
            selection_token,
            current_user.id,
            db,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    page_candidates = get_page_candidates(session)

    safe_pages = [
        {
            "id": page.get("id"),
            "name": page.get("name"),
            "tasks": page.get("tasks", []),
        }
        for page in page_candidates
    ]

    return {
        "pages": safe_pages,
        "selection_token": selection_token,
    }


@router.post("/connect")
def connect_facebook_pages(
    request_body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    selection_token = request_body.get("selection_token")
    selected_page_ids = request_body.get(
        "selected_page_ids",
        [],
    )

    # ---------------------------------------------------------
    # 1. Validate request
    # ---------------------------------------------------------
    if not selection_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="selection_token is required",
        )

    if not selected_page_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one page must be selected",
        )

    # ---------------------------------------------------------
    # 2. Validate selection session
    # ---------------------------------------------------------
    try:
        session = validate_facebook_selection_session(
            selection_token,
            current_user.id,
            db,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # ---------------------------------------------------------
    # 3. Get pages from server-side session
    # ---------------------------------------------------------
    page_candidates = get_page_candidates(session)

    page_map = {
        page["id"]: page
        for page in page_candidates
    }

    # ---------------------------------------------------------
    # 4. Validate every selected Page
    # ---------------------------------------------------------
    for page_id in selected_page_ids:
        if page_id not in page_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Page {page_id} "
                    f"not found in selection session"
                ),
            )

    # ---------------------------------------------------------
    # 5. Save selected Facebook Pages
    # ---------------------------------------------------------
    connected_count = 0

    for page_id in selected_page_ids:
        page = page_map[page_id]

        page_name = page.get("name")
        page_access_token = page.get("access_token")

        if not page_access_token:
            continue

        encrypted_token = encrypt_token(
            page_access_token
        )

        existing = db.scalar(
            select(SocialAccount)
            .where(
                SocialAccount.user_id == current_user.id
            )
            .where(
                SocialAccount.platform == "facebook"
            )
            .where(
                SocialAccount.account_id == page_id
            )
        )

        if existing:
            existing.access_token_encrypted = encrypted_token
            existing.account_name = page_name

        else:
            social_account = SocialAccount(
                user_id=current_user.id,
                platform="facebook",
                account_id=page_id,
                account_name=page_name,
                access_token_encrypted=encrypted_token,
            )

            db.add(social_account)

        connected_count += 1

    # ---------------------------------------------------------
    # 6. Mark selection session as used
    # ---------------------------------------------------------
    mark_selection_session_used(
        session,
        db,
    )

    db.commit()

    # ---------------------------------------------------------
    # 7. Log successful page connections
    # ---------------------------------------------------------
    if connected_count > 0:
        for page_id in selected_page_ids:
            if page_id in page_map:
                page = page_map[page_id]
                page_name = page.get("name")
                log_oauth_success(current_user.id, "facebook", page_name, request, db)

    # ---------------------------------------------------------
    # 8. Return result
    # ---------------------------------------------------------
    return {
        "platform": "facebook",
        "connected_pages": connected_count,
    }