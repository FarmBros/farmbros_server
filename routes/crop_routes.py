from typing import Annotated

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from models import runner
from controllers import crop_controller
from routes.user_routes import get_admin_user, get_current_user

router = APIRouter(
    prefix="/crops",
    tags=["Crop"]
)

security = HTTPBearer()


@router.post("/create", response_model=None)
async def create_crop(
        request: Request,
        user: Annotated[dict, Depends(get_admin_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Create a new crop (Admin only)"""
    data = await request.json()
    return await crop_controller.create_crop(
        session=session,
        data=data
    )


@router.post("/get", response_model=None)
async def get_crop(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Get a single crop by UUID (Authenticated users)"""
    data = await request.json()
    try:
        crop_id = data['crop_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="crop_id is required")

    return await crop_controller.get_crop(
        session=session,
        crop_id=crop_id
    )


@router.post("/get_all", response_model=None)
async def get_all_crops(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Get all crops with optional filtering (Authenticated users)"""
    data = await request.json()
    return await crop_controller.get_all_crops(
        session=session,
        skip=data.get('skip', 0),
        limit=data.get('limit', 100),
        crop_group=data.get('crop_group'),
        lifecycle=data.get('lifecycle')
    )


@router.post("/update", response_model=None)
async def update_crop(
        request: Request,
        user: Annotated[dict, Depends(get_admin_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Update a crop entry (Admin only)"""
    data = await request.json()
    try:
        crop_id = data['crop_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="crop_id is required")

    # Remove crop_id from data before passing to controller
    update_data = {k: v for k, v in data.items() if k != 'crop_id'}

    return await crop_controller.update_crop(
        session=session,
        crop_id=crop_id,
        data=update_data
    )


@router.post("/delete", response_model=None)
async def delete_crop(
        request: Request,
        user: Annotated[dict, Depends(get_admin_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Delete a crop entry (Admin only)"""
    data = await request.json()
    try:
        crop_id = data['crop_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="crop_id is required")

    return await crop_controller.delete_crop(
        session=session,
        crop_id=crop_id
    )


@router.post("/search", response_model=None)
async def search_crops(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Search crops by common name, genus, or species (Authenticated users)"""
    data = await request.json()
    try:
        search_term = data['search_term']
    except KeyError:
        raise HTTPException(status_code=400, detail="search_term is required")

    return await crop_controller.search_crops(
        session=session,
        search_term=search_term,
        skip=data.get('skip', 0),
        limit=data.get('limit', 50)
    )


@router.post("/count", response_model=None)
async def count_crops(
        request: Request,
        user: Annotated[dict, Depends(get_admin_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Count total crops with optional filtering (Admin only)"""
    data = await request.json()
    return await crop_controller.count_crops(
        session=session,
        crop_group=data.get('crop_group'),
        lifecycle=data.get('lifecycle')
    )


@router.post("/statistics", response_model=None)
async def get_crop_statistics(
        request: Request,
        user: Annotated[dict, Depends(get_admin_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Get statistics about crops in the database (Admin only)"""
    return await crop_controller.get_crop_statistics(
        session=session
    )


@router.post("/import_dataset", response_model=None)
async def import_crops_from_dataset(
        request: Request,
        user: Annotated[dict, Depends(get_admin_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    """Import crops from the dataset file (Admin only)"""
    data = await request.json()
    return await crop_controller.import_crops_from_dataset(
        session=session,
        file_path=data.get('file_path', 'assets/cropV2.json'),
        skip_existing=data.get('skip_existing', True)
    )