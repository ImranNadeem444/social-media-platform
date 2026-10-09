from datetime import datetime

from pydantic import BaseModel


class SocialAccountPublic(BaseModel):
    id: int
    platform: str
    account_id: str
    account_name: str | None
    token_expires_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
