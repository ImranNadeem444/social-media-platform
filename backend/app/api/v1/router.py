from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.social_accounts import router as social_accounts_router
from app.api.v1.instagram import router as instagram_router
from app.api.v1.facebook import router as facebook_router
from app.api.v1.posts import router as posts_router


api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(social_accounts_router)
api_router.include_router(instagram_router)
api_router.include_router(facebook_router)
api_router.include_router(posts_router)