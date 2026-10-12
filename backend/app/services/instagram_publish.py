
import asyncio
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
            print("[INSTAGRAM_API_TIMEOUT] /media request timed out")
            raise ValueError(
                "Instagram media creation request timed out (60s)."
            )

        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_info = error_data.get("error", {})
                error_msg = error_info.get("message", "Unknown error")
                error_code = error_info.get("code", "?")
                print(
                    f"[INSTAGRAM_API_ERROR] /media: "
                    f"{error_msg} (code {error_code})"
                )
                raise ValueError(
                    f"Instagram /media error (code {error_code}): {error_msg}"
                )
            except (json.JSONDecodeError, KeyError):
                pass

        response.raise_for_status()
        return response.json()


async def get_media_container_status(
    container_id: str,
    access_token: str,
) -> dict:
    """Fetch Instagram media container processing status."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"https://graph.instagram.com/{settings.GRAPH_API_VERSION}/{container_id}",
                params={
                    "fields": "status_code,status",
                    "access_token": access_token,
                },
            )
        except httpx.ReadTimeout:
            raise ValueError(
                "Timed out while checking Instagram media processing status."
            )

        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_info = error_data.get("error", {})
                error_msg = error_info.get("message", "Unknown error")
                error_code = error_info.get("code", "?")
                raise ValueError(
                    f"Instagram status check error (code {error_code}): "
                    f"{error_msg}"
                )
            except (json.JSONDecodeError, KeyError):
                pass

        response.raise_for_status()
        return response.json()


async def wait_for_media_container(
    container_id: str,
    access_token: str,
    max_attempts: int = 12,
    delay_seconds: int = 5,
) -> None:
    """Wait until Instagram finishes processing the media container."""
    for attempt in range(1, max_attempts + 1):
        result = await get_media_container_status(
            container_id=container_id,
            access_token=access_token,
        )

        status_code = result.get("status_code", "").upper()
        status_message = result.get("status", "")

        print(
            f"[INSTAGRAM_PUBLISH] Container {container_id}: "
            f"status_code={status_code or 'unknown'}, "
            f"status={status_message or 'unknown'} "
            f"(attempt {attempt}/{max_attempts})"
        )

        if status_code == "FINISHED":
            return

        if status_code in {"ERROR", "EXPIRED"}:
            raise ValueError(
                f"Instagram media processing failed: "
                f"{status_code}. {status_message}"
            )

        if attempt < max_attempts:
            await asyncio.sleep(delay_seconds)

    raise ValueError(
        f"Instagram media container {container_id} was not ready "
        f"after {max_attempts * delay_seconds} seconds."
    )


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
            print("[INSTAGRAM_API_TIMEOUT] /media_publish request timed out")
            raise ValueError(
                "Instagram media publish request timed out (60s)."
            )

        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_info = error_data.get("error", {})
                error_msg = error_info.get("message", "Unknown error")
                error_code = error_info.get("code", "?")
                print(
                    f"[INSTAGRAM_API_ERROR] /media_publish: "
                    f"{error_msg} (code {error_code})"
                )
                raise ValueError(
                    f"Instagram /media_publish error "
                    f"(code {error_code}): {error_msg}"
                )
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

    Waits for media processing to finish before publishing.
    Returns the published Instagram media ID.
    """
    try:
        access_token = decrypt_token(encrypted_token)
    except ValueError as e:
        raise ValueError(f"Failed to decrypt access token: {str(e)}")

    print(
        f"[INSTAGRAM_PUBLISH] Starting media container creation "
        f"for account {instagram_account_id}"
    )

    media_container_response = await create_media_container(
        instagram_account_id=instagram_account_id,
        image_url=image_url,
        caption=caption,
        access_token=access_token,
    )

    media_container_id = media_container_response.get("id")
    if not media_container_id:
        raise ValueError(
            f"Instagram did not return a media container ID: "
            f"{media_container_response}"
        )

    print(
        f"[INSTAGRAM_PUBLISH] Media container created: "
        f"{media_container_id}"
    )

    # Wait for Instagram to finish processing before publishing.
    await wait_for_media_container(
        container_id=media_container_id,
        access_token=access_token,
    )

    print(
        f"[INSTAGRAM_PUBLISH] Container ready. Publishing "
        f"{media_container_id}"
    )

    publish_response = await publish_media_container(
        instagram_account_id=instagram_account_id,
        media_container_id=media_container_id,
        access_token=access_token,
    )

    published_media_id = publish_response.get("id")
    if not published_media_id:
        raise ValueError(
            f"Instagram did not return a published media ID: "
            f"{publish_response}"
        )

    print(
        f"[INSTAGRAM_PUBLISH] Media published successfully: "
        f"{published_media_id}"
    )

    return published_media_id
