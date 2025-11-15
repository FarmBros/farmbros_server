from typing import Annotated

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from models import runner
from controllers import planted_crop_controller
from routes.user_routes import get_current_user

router = APIRouter(
    prefix="/planted_crops",
    tags=["Planted Crop"]
)

security = HTTPBearer()


@router.post("/create", response_model=None)
async def create_planted_crop(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Create a new planted crop (Authenticated users)"""
    data = await request.json()
    # Note: crop_id and plot_id in request body are UUIDs
    return await planted_crop_controller.create_planted_crop(
        session=session,
        user_uuid=user['uuid'],
        data=data
    )


@router.post("/get", response_model=None)
async def get_planted_crop(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Get a single planted crop by ID (UUID value) (Authenticated users)"""
    data = await request.json()
    try:
        planted_crop_uuid = data['planted_crop_id']  # Key is _id, value is UUID
    except KeyError:
        raise HTTPException(status_code=400, detail="planted_crop_id is required")

    return await planted_crop_controller.get_planted_crop(
        session=session,
        user_uuid=user['uuid'],
        planted_crop_uuid=planted_crop_uuid
    )


@router.post("/get_all", response_model=None)
async def get_all_planted_crops(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Get all planted crops with optional filtering (Authenticated users)"""
    data = await request.json()
    # Note: plot_id and crop_id in request body are UUIDs
    return await planted_crop_controller.get_all_planted_crops(
        session=session,
        user_uuid=user['uuid'],
        skip=data.get('skip', 0),
        limit=data.get('limit', 100),
        plot_uuid=data.get('plot_id'),
        crop_uuid=data.get('crop_id')
    )


@router.post("/get_with_details", response_model=None)
async def get_planted_crops_with_details(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Get planted crops with crop, plot, and user details (Authenticated users)"""
    data = await request.json()
    # Note: plot_id in request body is UUID
    return await planted_crop_controller.get_planted_crops_with_details(
        session=session,
        user_uuid=user['uuid'],
        skip=data.get('skip', 0),
        limit=data.get('limit', 100),
        plot_uuid=data.get('plot_id')
    )


@router.post("/update", response_model=None)
async def update_planted_crop(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Update a planted crop entry (Authenticated users)"""
    data = await request.json()
    try:
        planted_crop_uuid = data['planted_crop_id']  # Key is _id, value is UUID
    except KeyError:
        raise HTTPException(status_code=400, detail="planted_crop_id is required")

    # Remove planted_crop_id from data before passing to controller
    update_data = {k: v for k, v in data.items() if k != 'planted_crop_id'}

    return await planted_crop_controller.update_planted_crop(
        session=session,
        user_uuid=user['uuid'],
        planted_crop_uuid=planted_crop_uuid,
        data=update_data
    )


@router.post("/delete", response_model=None)
async def delete_planted_crop(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Delete a planted crop entry (Authenticated users)"""
    data = await request.json()
    try:
        planted_crop_uuid = data['planted_crop_id']  # Key is _id, value is UUID
    except KeyError:
        raise HTTPException(status_code=400, detail="planted_crop_id is required")

    return await planted_crop_controller.delete_planted_crop(
        session=session,
        user_uuid=user['uuid'],
        planted_crop_uuid=planted_crop_uuid
    )


@router.post("/count", response_model=None)
async def count_planted_crops(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Count planted crops with optional filtering (Authenticated users)"""
    data = await request.json()
    # Note: plot_id and crop_id in request body are UUIDs
    return await planted_crop_controller.count_planted_crops(
        session=session,
        user_uuid=user['uuid'],
        plot_uuid=data.get('plot_id'),
        crop_uuid=data.get('crop_id')
    )


@router.post("/statistics", response_model=None)
async def get_planted_crop_statistics(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Get statistics about planted crops (Authenticated users)"""
    return await planted_crop_controller.get_planted_crop_statistics(
        session=session,
        user_uuid=user['uuid']
    )
