from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from routes.user_routes import get_admin_user
from services.caching import clear_all_cache

router = APIRouter(
    prefix="/services",
    tags=["Services"]
)

security = HTTPBearer()


@router.post("/clear_cache", response_model=None)
async def clear_cache_endpoint(
        user: Annotated[dict, Depends(get_admin_user)],
):
    """
    Clear the entire Redis cache.
    Requires admin authentication.
    """
    success = await clear_all_cache()

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to clear cache"
        )

    return {
        "status": "success",
        "data": {"message": "Cache cleared successfully"},
        "error": None
    }