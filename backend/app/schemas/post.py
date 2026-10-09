from datetime import datetime

from pydantic import BaseModel


class PostCreate(BaseModel):
    social_account_id: int
    caption: str | None = None


class PostTargetResponse(BaseModel):
    id: int
    post_id: int
    social_account_id: int
    platform: str
    account_name: str | None
    account_id: str | None
    status: str
    platform_media_id: str | None
    platform_post_id: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class PostResponse(BaseModel):
    id: int
    user_id: int
    social_account_id: int
    platform: str
    caption: str | None
    image_path: str
    status: str
    instagram_media_id: str | None
    facebook_post_id: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class PostResponseWithTargets(BaseModel):
    id: int
    user_id: int
    caption: str | None
    image_path: str
    status: str
    targets: list[PostTargetResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }