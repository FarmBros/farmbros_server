from typing import Annotated

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from models import runner
from controllers import animal_type_controller
from routes.user_routes import get_admin_user, get_current_user

router = APIRouter(
    prefix="/animal_types",
    tags=["Animal Type"]
)

security = HTTPBearer()


@router.post("/create", response_model=None)
async def create_animal_type(
        request: Request,
        user: Annotated[dict, Depends(get_admin_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Create a new animal type (Admin only)"""
    data = await request.json()
    return await animal_type_controller.create_animal_type(
        session=session,
        data=data
    )


@router.post("/get", response_model=None)
async def get_animal_type(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Get a single animal type by UUID (Authenticated users)"""
    data = await request.json()
    try:
        animal_type_id = data['animal_type_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="animal_type_id is required")

    return await animal_type_controller.get_animal_type(
        session=session,
        animal_type_id=animal_type_id
    )


@router.post("/get_all", response_model=None)
async def get_all_animal_types(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Get all animal types with optional filtering (Authenticated users)"""
    data = await request.json()
    return await animal_type_controller.get_all_animal_types(
        session=session,
        skip=data.get('skip', 0),
        limit=data.get('limit', 100),
        category=data.get('category'),
        sex=data.get('sex')
    )


@router.post("/update", response_model=None)
async def update_animal_type(
        request: Request,
        user: Annotated[dict, Depends(get_admin_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Update an animal type entry (Admin only)"""
    data = await request.json()
    try:
        animal_type_id = data['animal_type_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="animal_type_id is required")

    # Remove animal_type_id from data before passing to controller
    update_data = {k: v for k, v in data.items() if k != 'animal_type_id'}

    return await animal_type_controller.update_animal_type(
        session=session,
        animal_type_id=animal_type_id,
        data=update_data
    )


@router.post("/delete", response_model=None)
async def delete_animal_type(
        request: Request,
        user: Annotated[dict, Depends(get_admin_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Delete an animal type entry (Admin only)"""
    data = await request.json()
    try:
        animal_type_id = data['animal_type_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="animal_type_id is required")

    return await animal_type_controller.delete_animal_type(
        session=session,
        animal_type_id=animal_type_id
    )
