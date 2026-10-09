import json

import httpx

from app.core.config import settings
from app.services.encryption import decrypt_token


async def publish_to_facebook(
    facebook_page_id: str,
    image_url: str,
    caption: str | None,
    encrypted_token: str,
) -> str:
    """
    Publish a single image post to a Facebook Page.

    The encrypted token must be the Page access token stored
    in the SocialAccount record.

    Returns:
        Facebook post/photo ID.
    """

    page_access_token = decrypt_token(encrypted_token)

    graph_version = settings.GRAPH_API_VERSION

    url = (
        f"https://graph.facebook.com/"
        f"{graph_version}/{facebook_page_id}/photos"
    )

    payload = {
        "url": image_url,
        "access_token": page_access_token,
    }

    if caption:
        payload["caption"] = caption

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                data=payload,
            )

    except httpx.RequestError as e:
        raise ValueError(
            f"Facebook API request failed: {str(e)}"
        ) from e

    # ---------------------------------------------------------
    # Handle Facebook API errors
    # ---------------------------------------------------------
    if response.status_code >= 400:
        error_message = "Facebook publishing failed"

        try:
            error_data = response.json()

            facebook_error = error_data.get("error", {})

            message = facebook_error.get("message")
            error_code = facebook_error.get("code")
            error_subcode = facebook_error.get("error_subcode")

            if message:
                error_message = f"Facebook API: {message}"

            if error_code is not None:
                error_message += f" (code {error_code})"

            if error_subcode is not None:
                error_message += f" (subcode {error_subcode})"

        except (ValueError, json.JSONDecodeError):
            error_message = (
                f"Facebook API returned HTTP "
                f"{response.status_code}"
            )

        raise ValueError(error_message)

    # ---------------------------------------------------------
    # Parse successful response
    # ---------------------------------------------------------
    try:
        response_data = response.json()
    except (ValueError, json.JSONDecodeError) as e:
        raise ValueError(
            "Facebook API returned an invalid response"
        ) from e

    post_id = (
        response_data.get("post_id")
        or response_data.get("id")
    )

    if not post_id:
        raise ValueError(
            "Facebook API did not return a post ID"
        )

    return str(post_id)