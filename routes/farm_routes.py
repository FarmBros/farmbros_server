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

@router.post("/get_farm", response_model=None)
async def get_farm(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
        ):
    data = await request.json()
    try:
        farm_id = data['farm_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="farm_id is required")

    return await farm_controller.get_farm(
        session=session,
        farm_id=farm_id,
        user=user,
        include_geojson=data.get('include_geojson', False)
    )

@router.post("/get_all_farms", response_model=None)
async def get_all_farms(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
        ):
    data = await request.json()
    return await farm_controller.get_all_farms(
        session=session,
        skip=data.get('skip', 0),
        limit=data.get('limit', 100),
        include_geojson=data.get('include_geojson', False)
    )

@router.post("/update_farm", response_model=None)
async def update_farm(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
        ):
    data = await request.json()
    try:
        farm_id = data['farm_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="farm_id is required")

    return await farm_controller.update_farm(
        session=session,
        farm_id=farm_id,
        name=data.get('name'),
        description=data.get('description'),
        boundary_geojson=data.get('boundary_geojson')
    )

@router.post("/delete_farm", response_model=None)
async def delete_farm(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
        ):
    data = await request.json()
    try:
        farm_id = data['farm_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="farm_id is required")

    return await farm_controller.delete_farm(
        session=session,
        farm_id=farm_id
    )

@router.post("/get_farm_stats", response_model=None)
async def get_farm_stats(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
        ):
    data = await request.json()
    return await farm_controller.get_farm_statistics(
        session=session,
        owner_id=data.get('owner_id')
    )