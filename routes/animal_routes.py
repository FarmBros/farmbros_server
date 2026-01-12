from typing import Annotated

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from models import runner
from controllers import animal_controller
from routes.user_routes import get_current_user

router = APIRouter(
    prefix="/animals",
    tags=["Animal"]
)

security = HTTPBearer()


@router.post("/create", response_model=None)
async def create_animal(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Create a new animal (Authenticated users)"""
    data = await request.json()
    # Note: farm_id, plot_id, and animal_type_id in request body are UUIDs
    return await animal_controller.create_animal(
        session=session,
        user_uuid=user['uuid'],
        data=data
    )


@router.post("/get", response_model=None)
async def get_animal(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Get a single animal by ID (UUID value) (Authenticated users)"""
    data = await request.json()
    try:
        animal_uuid = data['animal_id']  # Key is _id, value is UUID
    except KeyError:
        raise HTTPException(status_code=400, detail="animal_id is required")

    return await animal_controller.get_animal(
        session=session,
        user_uuid=user['uuid'],
        animal_uuid=animal_uuid
    )


@router.post("/get_all", response_model=None)
async def get_all_animals(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Get all animals with optional filtering (Authenticated users)"""
    data = await request.json()
    # Note: farm_id and animal_type_id in request body are UUIDs
    return await animal_controller.get_all_animals(
        session=session,
        user_uuid=user['uuid'],
        skip=data.get('skip', 0),
        limit=data.get('limit', 100),
        farm_id=data.get('farm_id'),
        animal_type_id=data.get('animal_type_id'),
        is_active=data.get('is_active')
    )


@router.post("/update", response_model=None)
async def update_animal(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Update an animal entry (Authenticated users)"""
    data = await request.json()
    try:
        animal_uuid = data['animal_id']  # Key is _id, value is UUID
    except KeyError:
        raise HTTPException(status_code=400, detail="animal_id is required")

    # Remove animal_id from data before passing to controller
    update_data = {k: v for k, v in data.items() if k != 'animal_id'}

    return await animal_controller.update_animal(
        session=session,
        user_uuid=user['uuid'],
        animal_uuid=animal_uuid,
        data=update_data
    )


@router.post("/delete", response_model=None)
async def delete_animal(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Delete an animal entry (Authenticated users)"""
    data = await request.json()
    try:
        animal_uuid = data['animal_id']  # Key is _id, value is UUID
    except KeyError:
        raise HTTPException(status_code=400, detail="animal_id is required")

    return await animal_controller.delete_animal(
        session=session,
        user_uuid=user['uuid'],
        animal_uuid=animal_uuid
    )
