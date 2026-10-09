from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.dependencies import get_current_user
from app.core.rate_limiting import limiter
from app.core.security_logger import log_post_created, log_post_failure
from app.db.database import get_db
from app.models.post import Post
from app.models.post_target import PostTarget
from app.models.social_account import SocialAccount
from app.models.user import User
from app.schemas.post import PostResponseWithTargets
from app.services.multi_account_publish import publish_to_multiple_accounts
from app.services.file_storage import delete_file, generate_public_url, save_upload


router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.post("", response_model=PostResponseWithTargets, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")
async def create_post(
    request: Request,
    target: str = Form(...),
    caption: str | None = Form(None),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create and publish a post to multiple social media accounts.

    Args:
        target: "instagram", "facebook", or "all"
        caption: Optional caption/description
        image: Image file to upload

    Returns:
        PostResponseWithTargets with list of targets and their individual statuses.

    Behavior:
        - target="instagram": publishes to ALL connected Instagram accounts
        - target="facebook": publishes to ALL connected Facebook pages
        - target="all": publishes to ALL connected Instagram and Facebook accounts

    Each target publishes independently. If one fails, others continue.
    """

    # Validate target parameter
    target = target.lower()
    if target not in {"instagram", "facebook", "all"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target must be 'instagram', 'facebook', or 'all'",
        )

    # ---------------------------------------------------------
    # 1. Read uploaded image
    # ---------------------------------------------------------
    try:
        file_content = await image.read()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(e)}",
        )

    # ---------------------------------------------------------
    # 2. Save uploaded file
    # ---------------------------------------------------------
    try:
        filename = save_upload(
            file_content,
            image.filename or "image.jpg",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # ---------------------------------------------------------
    # 3. Generate public URL
    # ---------------------------------------------------------
    image_url = generate_public_url(filename)

    # ---------------------------------------------------------
    # 4. Publish to multiple accounts
    # ---------------------------------------------------------
    try:
        post, post_targets = await publish_to_multiple_accounts(
            user_id=current_user.id,
            target_platform=target,
            image_url=image_url,
            caption=caption,
            db=db,
        )

        # Update post with the saved image path
        post.image_path = filename

        db.commit()
        db.refresh(post)

        # Refresh targets to get database-generated timestamps
        for target in post_targets:
            db.refresh(target)

        # Enrich targets with account names
        enriched_targets = []
        for target in post_targets:
            social_account = db.scalar(
                select(SocialAccount).where(
                    SocialAccount.id == target.social_account_id
                )
            )

            enriched_targets.append({
                "id": target.id,
                "post_id": target.post_id,
                "social_account_id": target.social_account_id,
                "platform": target.platform,
                "account_name": social_account.account_name if social_account else None,
                "account_id": social_account.account_id if social_account else None,
                "status": target.status,
                "platform_media_id": target.platform_media_id,
                "platform_post_id": target.platform_post_id,
                "error_message": target.error_message,
                "created_at": target.created_at,
                "updated_at": target.updated_at,
            })

        log_post_created(
            current_user.id,
            target,
            len(post_targets),
            post.status,
            request,
            db,
        )

        return {
            "id": post.id,
            "user_id": post.user_id,
            "caption": post.caption,
            "image_path": post.image_path,
            "status": post.status,
            "targets": enriched_targets,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
        }

    except ValueError as e:
        # No accounts found or invalid platform
        error_message = str(e)

        print(
            f"[PUBLISH_ERROR] "
            f"UserID={current_user.id} "
            f"Target={target} "
            f"ValueError: {error_message}"
        )

        log_post_failure(current_user.id, error_message, request, db)

        # Clean up uploaded file
        try:
            delete_file(filename)
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )

    except Exception as e:
        # Unexpected error
        import traceback

        error_type = type(e).__name__
        error_str = str(e)

        print(
            f"[PUBLISH_ERROR] "
            f"UserID={current_user.id} "
            f"Target={target} "
            f"{error_type}: {error_str}"
        )

        print(
            f"[PUBLISH_TRACEBACK]\n"
            f"{traceback.format_exc()}"
        )

        log_post_failure(current_user.id, f"{error_type}: {error_str}", request, db)

        # Clean up uploaded file
        try:
            delete_file(filename)
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while publishing",
        )