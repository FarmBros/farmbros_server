from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, text, select
from shapely.geometry import shape, Point, Polygon
import json
from datetime import datetime
import uuid as uuid_lib

from models.farm import Farm
from models.user import User


async def create_farm(
        session: AsyncSession,
        data: Dict[str, Any],
        user: Dict[str, Any]
) -> Farm:
    try:
        name = data.get("name")
        description = data.get("description", "")
        owner_id = user["uuid"]
        boundary_geojson = data["geojson"]

        boundary_shape = shape(boundary_geojson)

        if not isinstance(boundary_shape, Polygon):
            raise ValueError("Boundary must be a Polygon")

        centroid = boundary_shape.centroid

        farm = Farm(
            name=name,
            owner_id=owner_id,
            description=description
        )

        farm.boundary = func.ST_GeomFromText(boundary_shape.wkt, 4326)
        farm.centroid = func.ST_GeomFromText(centroid.wkt, 4326)

        session.add(farm)
        await session.flush()

        area_result = await session.execute(
            select(func.ST_Area(Farm.boundary)).filter(Farm.id == farm.id)
        )
        area_query = area_result.scalar()

        farm.area_sqm = area_query

        await session.commit()
        await session.refresh(farm)

        return farm.to_dict()

    except Exception as e:
        await session.rollback()
        raise Exception(f"Error creating farm: {str(e)}")


async def get_farm(
        session: AsyncSession,
        farm_id: Optional[int] = None,
        farm_uuid: Optional[str] = None,
        include_geojson: bool = True
) -> Optional[Farm]:
    query = select(Farm)

    if farm_id:
        query = query.filter(Farm.id == farm_id)
    elif farm_uuid:
        query = query.filter(Farm.uuid == farm_uuid)
    else:
        return None

    result = await session.execute(query)
    farm = result.scalar_one_or_none()

    if farm and include_geojson:
        farm.boundary_geojson = await get_boundary_as_geojson(session, farm.id)
        farm.centroid_geojson = await get_centroid_as_geojson(session, farm.id)

    return farm


async def get_farms_by_owner(
        session: AsyncSession,
        owner_id: int,
        include_geojson: bool = True,
        skip: int = 0,
        limit: int = 100
) -> List[Farm]:
    query = select(Farm).filter(
        Farm.owner_id == owner_id
    ).offset(skip).limit(limit)

    result = await session.execute(query)
    farms = result.scalars().all()

    if include_geojson:
        for farm in farms:
            farm.boundary_geojson = await get_boundary_as_geojson(session, farm.id)
            farm.centroid_geojson = await get_centroid_as_geojson(session, farm.id)

    return farms


async def get_all_farms(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        include_geojson: bool = False
) -> List[Farm]:
    query = select(Farm).offset(skip).limit(limit)
    result = await session.execute(query)
    farms = result.scalars().all()

    if include_geojson:
        for farm in farms:
            farm.boundary_geojson = await get_boundary_as_geojson(session, farm.id)
            farm.centroid_geojson = await get_centroid_as_geojson(session, farm.id)

    return farms


async def update_farm(
        session: AsyncSession,
        farm_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        boundary_geojson: Optional[Dict[str, Any]] = None
) -> Optional[Farm]:
    query = select(Farm).filter(Farm.id == farm_id)
    result = await session.execute(query)
    farm = result.scalar_one_or_none()

    if not farm:
        return None

    try:
        if name is not None:
            farm.name = name

        if description is not None:
            farm.description = description

        if boundary_geojson is not None:
            boundary_shape = shape(boundary_geojson)

            if not isinstance(boundary_shape, Polygon):
                raise ValueError("Boundary must be a Polygon")

            farm.boundary = func.ST_GeomFromText(boundary_shape.wkt, 4326)
            farm.centroid = func.ST_GeomFromText(boundary_shape.centroid.wkt, 4326)

            await session.flush()

            area_result = await session.execute(
                select(func.ST_Area(Farm.boundary)).filter(Farm.id == farm.id)
            )
            area_query = area_result.scalar()
            farm.area_sqm = area_query

        farm.update_timestamp()

        await session.commit()
        await session.refresh(farm)

        farm.boundary_geojson = await get_boundary_as_geojson(session, farm.id)
        farm.centroid_geojson = await get_centroid_as_geojson(session, farm.id)

        return farm

    except Exception as e:
        await session.rollback()
        raise Exception(f"Error updating farm: {str(e)}")


async def delete_farm(session: AsyncSession, farm_id: int) -> bool:
    query = select(Farm).filter(Farm.id == farm_id)
    result = await session.execute(query)
    farm = result.scalar_one_or_none()

    if not farm:
        return False

    try:
        await session.delete(farm)
        await session.commit()
        return True
    except Exception as e:
        await session.rollback()
        raise Exception(f"Error deleting farm: {str(e)}")


async def get_farms_within_area(
        session: AsyncSession,
        center_lng: float,
        center_lat: float,
        radius_meters: float,
        limit: int = 50
) -> List[Farm]:
    center_point = func.ST_GeomFromText(f'POINT({center_lng} {center_lat})', 4326)

    query = select(Farm).filter(
        func.ST_DWithin(
            Farm.centroid,
            center_point,
            radius_meters
        )
    ).limit(limit)

    result = await session.execute(query)
    farms = result.scalars().all()

    for farm in farms:
        farm.boundary_geojson = await get_boundary_as_geojson(session, farm.id)
        farm.centroid_geojson = await get_centroid_as_geojson(session, farm.id)

    return farms


async def get_farms_intersecting_polygon(
        session: AsyncSession,
        polygon_geojson: Dict[str, Any],
        limit: int = 50
) -> List[Farm]:
    polygon_shape = shape(polygon_geojson)
    polygon_wkt = func.ST_GeomFromText(polygon_shape.wkt, 4326)

    query = select(Farm).filter(
        func.ST_Intersects(
            Farm.boundary,
            polygon_wkt
        )
    ).limit(limit)

    result = await session.execute(query)
    farms = result.scalars().all()

    for farm in farms:
        farm.boundary_geojson = await get_boundary_as_geojson(session, farm.id)
        farm.centroid_geojson = await get_centroid_as_geojson(session, farm.id)

    return farms


async def calculate_total_area_by_owner(session: AsyncSession, owner_id: int) -> float:
    query = select(func.sum(Farm.area_sqm)).filter(Farm.owner_id == owner_id)
    result = await session.execute(query)
    total_area = result.scalar()

    return total_area or 0.0


async def count_farms_by_owner(session: AsyncSession, owner_id: int) -> int:
    query = select(func.count(Farm.id)).filter(Farm.owner_id == owner_id)
    result = await session.execute(query)
    return result.scalar()


async def get_boundary_as_geojson(session: AsyncSession, farm_id: int) -> Optional[Dict]:
    query = select(func.ST_AsGeoJSON(Farm.boundary)).filter(Farm.id == farm_id)
    result = await session.execute(query)
    geojson = result.scalar()

    return json.loads(geojson) if geojson else None


async def get_centroid_as_geojson(session: AsyncSession, farm_id: int) -> Optional[Dict]:
    query = select(func.ST_AsGeoJSON(Farm.centroid)).filter(Farm.id == farm_id)
    result = await session.execute(query)
    geojson = result.scalar()

    return json.loads(geojson) if geojson else None


def validate_geojson_polygon(geojson_data: Dict[str, Any]) -> bool:
    try:
        if geojson_data.get('type') != 'Polygon':
            return False

        coords = geojson_data.get('coordinates', [])
        if not coords or not coords[0]:
            return False

        if coords[0][0] != coords[0][-1]:
            return False

        if len(coords[0]) < 4:
            return False

        polygon = shape(geojson_data)

        return polygon.is_valid

    except Exception:
        return False


async def get_farm_statistics(session: AsyncSession, owner_id: Optional[int] = None) -> Dict[str, Any]:
    count_query = select(func.count(Farm.id))

    if owner_id:
        count_query = count_query.filter(Farm.owner_id == owner_id)

    count_result = await session.execute(count_query)
    total_farms = count_result.scalar()

    if total_farms == 0:
        return {
            'total_farms': 0,
            'total_area_sqm': 0,
            'total_area_hectares': 0,
            'average_area_sqm': 0,
            'smallest_farm_sqm': 0,
            'largest_farm_sqm': 0
        }

    stats_query = select(
        func.sum(Farm.area_sqm).label('total_area'),
        func.avg(Farm.area_sqm).label('avg_area'),
        func.min(Farm.area_sqm).label('min_area'),
        func.max(Farm.area_sqm).label('max_area')
    )

    if owner_id:
        stats_query = stats_query.filter(Farm.owner_id == owner_id)

    stats_result = await session.execute(stats_query)
    result = stats_result.first()

    return {
        'total_farms': total_farms,
        'total_area_sqm': float(result.total_area or 0),
        'total_area_hectares': float(result.total_area or 0) / 10000,
        'average_area_sqm': float(result.avg_area or 0),
        'smallest_farm_sqm': float(result.min_area or 0),
        'largest_farm_sqm': float(result.max_area or 0)
    }