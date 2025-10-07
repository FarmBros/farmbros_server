from typing import Annotated

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from models import runner
from controllers import plot_controller
from routes.user_routes import get_current_user

router = APIRouter(
    prefix="/plots",
    tags=["Plot"]
)

security = HTTPBearer()


@router.post("/create", response_model=None)
async def create_plot(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    data = await request.json()
    return await plot_controller.create_plot(
        session=session,
        data=data,
        user=user
    )


@router.post("/get_plot", response_model=None)
async def get_plot(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    data = await request.json()
    try:
        plot_id = data['plot_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="plot_id is required")

    return await plot_controller.get_plot(
        session=session,
        user=user,
        plot_id=plot_id,
        include_geojson=data.get('include_geojson', True)
    )


@router.post("/get_plots_by_farm", response_model=None)
async def get_plots_by_farm(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    data = await request.json()
    try:
        farm_id = data['farm_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="farm_id is required")

    return await plot_controller.get_plots_by_farm(
        session=session,
        farm_id=farm_id,
        include_geojson=data.get('include_geojson', True),
        skip=data.get('skip', 0),
        limit=data.get('limit', 100)
    )


@router.post("/get_user_plots", response_model=None)
async def get_user_plots(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    data = await request.json()
    return await plot_controller.get_plots_by_user(
        session=session,
        user_id=user['uuid'],
        include_geojson=data.get('include_geojson', True),
        skip=data.get('skip', 0),
        limit=data.get('limit', 100)
    )


@router.post("/get_plots_by_type", response_model=None)
async def get_plots_by_type(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    data = await request.json()
    try:
        plot_type = data['plot_type']
    except KeyError:
        raise HTTPException(status_code=400, detail="plot_type is required")

    return await plot_controller.get_plots_by_type(
        session=session,
        user_id=user['uuid'],
        plot_type=plot_type,
        include_geojson=data.get('include_geojson', True),
        skip=data.get('skip', 0),
        limit=data.get('limit', 100)
    )


@router.post("/update_plot", response_model=None)
async def update_plot(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    data = await request.json()
    try:
        plot_id = data['plot_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="plot_id is required")

    return await plot_controller.update_plot(
        session=session,
        plot_id=plot_id,
        user=user,
        name=data.get('name'),
        plot_number=data.get('plot_number'),
        plot_type=data.get('plot_type'),
        notes=data.get('notes'),
        boundary_geojson=data.get('boundary_geojson'),
        plot_type_data=data.get('plot_type_data')
    )


@router.post("/delete_plot", response_model=None)
async def delete_plot(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    data = await request.json()
    try:
        plot_id = data['plot_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="plot_id is required")

    return await plot_controller.delete_plot(
        session=session,
        plot_id=plot_id,
        user=user
    )


@router.post("/count_plots_by_farm", response_model=None)
async def count_plots_by_farm(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    data = await request.json()
    try:
        farm_id = data['farm_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="farm_id is required")

    return await plot_controller.count_plots_by_farm(
        session=session,
        farm_id=farm_id
    )


@router.post("/get_plot_area_by_farm", response_model=None)
async def get_plot_area_by_farm(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    data = await request.json()
    try:
        farm_id = data['farm_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="farm_id is required")

    return await plot_controller.calculate_total_plot_area_by_farm(
        session=session,
        farm_id=farm_id
    )


@router.post("/get_plot_stats", response_model=None)
async def get_plot_stats(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    data = await request.json()
    return await plot_controller.get_plot_statistics(
        session=session,
        user_id=data.get('user_id'),
        farm_id=data.get('farm_id')
    )


@router.post("/get_plot_type_data", response_model=None)
async def get_plot_type_data(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    data = await request.json()
    try:
        plot_id = data['plot_id']
    except KeyError:
        raise HTTPException(status_code=400, detail="plot_id is required")

    return await plot_controller.get_plot_with_type_data(
        session=session,
        user=user,
        plot_id=plot_id
    )


@router.post("/update_plot_type_data", response_model=None)
async def update_plot_type_data(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: AsyncSession = Depends(runner.get_db_session),
):
    data = await request.json()
    try:
        plot_id = data['plot_id']
        plot_type_data = data['plot_type_data']
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"{e.args[0]} is required")

    return await plot_controller.update_plot_type_data_only(
        session=session,
        user=user,
        plot_id=plot_id,
        plot_type_data=plot_type_data
    )