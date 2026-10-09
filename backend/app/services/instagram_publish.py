import httpx
import json

from app.core.config import settings
from app.services.encryption import decrypt_token


async def create_media_container(
    instagram_account_id: str,
    image_url: str,
    caption: str | None,
    access_token: str,
) -> dict:
    """Create an Instagram media container for the image."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "image_url": image_url,
            "caption": caption or "",
            "access_token": access_token,
        }

        try:
            response = await client.post(
                f"https://graph.instagram.com/{settings.GRAPH_API_VERSION}/{instagram_account_id}/media",
                json=payload,
            )
        except httpx.ReadTimeout:
            print(f"[INSTAGRAM_API_TIMEOUT] /media endpoint took longer than 60 seconds to respond")
            raise ValueError("Instagram media creation request timed out (60s). API may be experiencing delays.")

        # Check for errors before raising
        if response.status_code >= 400:
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_info = error_data["error"]
                    error_msg = error_info.get("message", "Unknown error")
                    error_code = error_info.get("code", "?")
                    print(f"[INSTAGRAM_API_ERROR] /media: {error_msg} (code {error_code})")
                    raise ValueError(f"Instagram /media error (code {error_code}): {error_msg}")
            except (json.JSONDecodeError, KeyError):
                pass

        response.raise_for_status()
        return response.json()


async def publish_media_container(
    instagram_account_id: str,
    media_container_id: str,
    access_token: str,
) -> dict:
    """Publish an Instagram media container."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "creation_id": media_container_id,
            "access_token": access_token,
        }

        try:
            response = await client.post(
                f"https://graph.instagram.com/{settings.GRAPH_API_VERSION}/{instagram_account_id}/media_publish",
                json=payload,
            )
        except httpx.ReadTimeout:
            print(f"[INSTAGRAM_API_TIMEOUT] /media_publish endpoint took longer than 60 seconds to respond")
            raise ValueError("Instagram media publish request timed out (60s). API may be experiencing delays.")

        # Check for errors before raising
        if response.status_code >= 400:
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_info = error_data["error"]
                    error_msg = error_info.get("message", "Unknown error")
                    error_code = error_info.get("code", "?")
                    print(f"[INSTAGRAM_API_ERROR] /media_publish: {error_msg} (code {error_code})")
                    raise ValueError(f"Instagram /media_publish error (code {error_code}): {error_msg}")
            except (json.JSONDecodeError, KeyError):
                pass

        response.raise_for_status()
        return response.json()


async def publish_to_instagram(
    instagram_account_id: str,
    image_url: str,
    caption: str | None,
    encrypted_token: str,
) -> str:
    """
    Publish an image to Instagram.

    Returns the Instagram media ID if successful.
    Raises an exception if publishing fails.
    """
    try:
        access_token = decrypt_token(encrypted_token)
    except ValueError as e:
        raise ValueError(f"Failed to decrypt access token: {str(e)}")

    print(f"[INSTAGRAM_PUBLISH] Starting media container creation for account {instagram_account_id}")
    media_container_response = await create_media_container(
        instagram_account_id=instagram_account_id,
        image_url=image_url,
        caption=caption,
        access_token=access_token,
    )

    if "id" not in media_container_response:
        raise ValueError(
            f"Failed to create media container: {media_container_response}"
        )

    media_container_id = media_container_response["id"]
    print(f"[INSTAGRAM_PUBLISH] Media container created: {media_container_id}")

    print(f"[INSTAGRAM_PUBLISH] Publishing media container {media_container_id}")
    publish_response = await publish_media_container(
        instagram_account_id=instagram_account_id,
        media_container_id=media_container_id,
        access_token=access_token,
    )

    if "id" not in publish_response:
        raise ValueError(
            f"Failed to publish media: {publish_response}"
        )

    published_media_id = publish_response["id"]
    print(f"[INSTAGRAM_PUBLISH] Media published successfully: {published_media_id}")
    return published_media_id
