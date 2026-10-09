from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.security_logger import log_account_disconnect
from app.db.database import get_db
from app.models.social_account import SocialAccount
from app.models.user import User
from app.schemas.social_account import SocialAccountPublic


router = APIRouter(
    prefix="/social-accounts",
    tags=["Social Accounts"],
)


@router.get("", response_model=list[SocialAccountPublic])
def get_my_social_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accounts = db.scalars(
        select(SocialAccount)
        .where(SocialAccount.user_id == current_user.id)
        .order_by(SocialAccount.created_at.desc())
    ).all()

    return accounts


@router.delete("/{social_account_id}", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_social_account(
    social_account_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.scalar(
        select(SocialAccount).where(SocialAccount.id == social_account_id)
    )

    if not account or account.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # Log before deletion
    log_account_disconnect(
        current_user.id,
        account.id,
        account.platform,
        account.account_name,
        request,
        db,
    )

    db.delete(account)
    db.commit()