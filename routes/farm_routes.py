from typing import Annotated

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from models import runner
from controllers import farm_controller
from routes.user_routes import get_current_user

router = APIRouter(
    prefix="/farms",
    tags=["Farm"]
)

security = HTTPBearer()


@router.post("/create", response_model=None)
async def create_farm(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
        ):
    data = await request.json()
    return await farm_controller.create_farm(
        session=session,
        data=data,
        user=user
    )
