"""
Multi-account publishing orchestration service.

Handles publishing to multiple social accounts independently with error isolation.
Reuses existing instagram_publish.py and facebook_publish.py services.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.post import Post
from app.models.post_target import PostTarget
from app.models.social_account import SocialAccount
from app.services.instagram_publish import publish_to_instagram
from app.services.facebook_publish import publish_to_facebook


async def publish_to_multiple_accounts(
    user_id: int,
    target_platform: str,
    image_url: str,
    caption: str | None,
    db: Session,
) -> tuple[Post, list[PostTarget]]:
    """
    Publish to multiple social accounts based on target platform.

    Args:
        user_id: Current authenticated user ID
        target_platform: "instagram", "facebook", or "all"
        image_url: Public URL of the uploaded image
        caption: Caption/description
        db: Database session

    Returns:
        Tuple of (Post, list[PostTarget])
        Each PostTarget has its own status and error_message.
        If one target fails, others continue publishing.
    """

    # Normalize platform selection
    target_platform = target_platform.lower()

    # Find all applicable social accounts for this user
    if target_platform == "instagram":
        eligible_platforms = ["instagram"]
    elif target_platform == "facebook":
        eligible_platforms = ["facebook"]
    elif target_platform == "all":
        eligible_platforms = ["instagram", "facebook"]
    else:
        raise ValueError(
            f"Invalid target platform: {target_platform}. "
            f"Must be 'instagram', 'facebook', or 'all'."
        )

    # Query all user's social accounts matching the target platform(s)
    social_accounts = db.scalars(
        select(SocialAccount).where(
            SocialAccount.user_id == user_id,
            SocialAccount.platform.in_(eligible_platforms),
        )
    ).all()

    if not social_accounts:
        platform_names = " or ".join(eligible_platforms)
        raise ValueError(
            f"No connected {platform_names} accounts found for this user."
        )

    # Create the main Post record
    post = Post(
        user_id=user_id,
        # Keep social_account_id as first account for backward compatibility
        social_account_id=social_accounts[0].id,
        platform=social_accounts[0].platform,
        caption=caption,
        image_path="",  # Will be set by caller
        status="publishing",
    )

    db.add(post)
    db.flush()  # Get post ID without committing

    # Create PostTarget for each eligible account
    post_targets = []
    for social_account in social_accounts:
        target = PostTarget(
            post_id=post.id,
            social_account_id=social_account.id,
            platform=social_account.platform,
            status="pending",
        )
        db.add(target)
        post_targets.append(target)

    db.flush()  # Save targets

    # Publish to each target independently
    for target in post_targets:
        try:
            await _publish_to_target(target, social_accounts, image_url, caption, db)
        except Exception as e:
            # Log error but continue publishing to other targets
            target.status = "failed"
            target.error_message = str(e)
            print(
                f"[PUBLISH_ERROR] "
                f"Target ID {target.id} "
                f"Platform={target.platform} "
                f"SocialAccountID={target.social_account_id} "
                f"Error: {str(e)}"
            )

    # Update overall post status based on target results
    target_statuses = [t.status for t in post_targets]
    if all(status == "published" for status in target_statuses):
        post.status = "published"
    elif all(status == "failed" for status in target_statuses):
        post.status = "failed"
    else:
        post.status = "partial"

    return post, post_targets


async def _publish_to_target(
    target: PostTarget,
    social_accounts: list[SocialAccount],
    image_url: str,
    caption: str | None,
    db: Session,
) -> None:
    """
    Publish to a single target account.

    Raises ValueError if publishing fails.
    Updates target status/IDs/errors on the target object.
    """

    # Find the social account for this target
    social_account = next(
        (acc for acc in social_accounts if acc.id == target.social_account_id),
        None,
    )

    if not social_account:
        raise ValueError("Social account not found for this target")

    target.status = "publishing"

    platform = social_account.platform.lower()

    try:
        if platform == "instagram":
            media_id = await publish_to_instagram(
                instagram_account_id=social_account.account_id,
                image_url=image_url,
                caption=caption,
                encrypted_token=social_account.access_token_encrypted,
            )
            target.platform_media_id = media_id
            target.status = "published"

        elif platform == "facebook":
            post_id = await publish_to_facebook(
                facebook_page_id=social_account.account_id,
                image_url=image_url,
                caption=caption,
                encrypted_token=social_account.access_token_encrypted,
            )
            target.platform_post_id = post_id
            target.status = "published"

        else:
            raise ValueError(f"Unsupported platform: {platform}")

    except ValueError as e:
        # Re-raise ValueError (already sanitized from service layer)
        raise

    except Exception as e:
        # Wrap unexpected errors
        error_type = type(e).__name__
        error_str = str(e)

        # Try to extract useful API error information
        if hasattr(e, "response"):
            try:
                import json

                error_data = json.loads(e.response.text)

                if "error" in error_data:
                    api_error = error_data["error"].get(
                        "message",
                        "Unknown API error",
                    )

                    error_str = (
                        f"{platform.capitalize()} API: "
                        f"{api_error}"
                    )

            except Exception:
                pass

        raise ValueError(error_str if error_str else f"Publishing failed: {error_type}")
