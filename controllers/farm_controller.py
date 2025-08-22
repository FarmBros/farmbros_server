import json
from typing import List, Optional, Dict, Any

from shapely.geometry import shape, Polygon
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.farm import Farm


async def create_farm(
        session: AsyncSession,
        data: Dict[str, Any],
        user: Dict[str, Any]
) -> Dict[str, Any]:
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

        return {
            "status": "success",
            "data": farm.to_dict(),
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_farm(
        session: AsyncSession,
        user: Dict[str, Any],
        farm_id: Optional[str] = None,
        include_geojson: bool = True
) -> Dict[str, Any]:
    try:
        query = select(Farm)

        query = query.filter(Farm.uuid == farm_id)

        result = await session.execute(query)
        farm = result.scalar_one_or_none()

        if not farm:
            return {
                "status": "error",
                "data": None,
                "error": "Farm not found"
            }

        if include_geojson:
            farm.boundary_geojson = await get_boundary_as_geojson(session, farm.id)
            farm.centroid_geojson = await get_centroid_as_geojson(session, farm.id)

        return {
            "status": "success",
            "data": farm.to_dict(include_geometry=include_geojson),
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_farms_by_owner(
        session: AsyncSession,
        owner_id: str,
        include_geojson: bool = True,
        skip: int = 0,
        limit: int = 100
) -> Dict[str, Any]:
    try:
        query = select(Farm).filter(
            Farm.owner_id == owner_id
        ).offset(skip).limit(limit)

        result = await session.execute(query)
        farms = result.scalars().all()

        if include_geojson:
            for farm in farms:
                farm.boundary_geojson = await get_boundary_as_geojson(session, farm.id)
                farm.centroid_geojson = await get_centroid_as_geojson(session, farm.id)

        return {
            "status": "success",
            "data": [farm.to_dict(include_geometry=include_geojson) for farm in farms],
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_all_farms(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        include_geojson: bool = False
) -> Dict[str, Any]:
    try:
        query = select(Farm).offset(skip).limit(limit)
        result = await session.execute(query)
        farms = result.scalars().all()

        if include_geojson:
            for farm in farms:
                farm.boundary_geojson = await get_boundary_as_geojson(session, farm.id)
                farm.centroid_geojson = await get_centroid_as_geojson(session, farm.id)

        return {
            "status": "success",
            "data": [farm.to_dict(include_geometry=include_geojson) for farm in farms],
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def update_farm(
        session: AsyncSession,
        farm_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        boundary_geojson: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    try:
        query = select(Farm).filter(Farm.uuid == farm_id)
        result = await session.execute(query)
        farm = result.scalar_one_or_none()

        if not farm:
            return {
                "status": "error",
                "data": None,
                "error": "Farm not found"
            }

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

        return {
            "status": "success",
            "data": farm.to_dict(include_geometry=True),
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def delete_farm(session: AsyncSession, farm_id: str) -> Dict[str, Any]:
    try:
        query = select(Farm).filter(Farm.uuid == farm_id)
        result = await session.execute(query)
        farm = result.scalar_one_or_none()

        if not farm:
            return {
                "status": "error",
                "data": None,
                "error": "Farm not found"
            }

        await session.delete(farm)
        await session.commit()
        
        return {
            "status": "success",
            "data": {"deleted": True, "farm_id": farm_id},
            "error": None
        }
        
    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_farms_within_area(
        session: AsyncSession,
        center_lng: float,
        center_lat: float,
        radius_meters: float,
        limit: int = 50
) -> Dict[str, Any]:
    try:
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

        return {
            "status": "success",
            "data": [farm.to_dict(include_geometry=True) for farm in farms],
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_farms_intersecting_polygon(
        session: AsyncSession,
        polygon_geojson: Dict[str, Any],
        limit: int = 50
) -> Dict[str, Any]:
    try:
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

        return {
            "status": "success",
            "data": [farm.to_dict(include_geometry=True) for farm in farms],
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def calculate_total_area_by_owner(session: AsyncSession, owner_id: str) -> Dict[str, Any]:
    try:
        query = select(func.sum(Farm.area_sqm)).filter(Farm.owner_id == owner_id)
        result = await session.execute(query)
        total_area = result.scalar()

        return {
            "status": "success",
            "data": {"total_area_sqm": total_area or 0.0},
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def count_farms_by_owner(session: AsyncSession, owner_id: str) -> Dict[str, Any]:
    try:
        query = select(func.count(Farm.id)).filter(Farm.owner_id == owner_id)
        result = await session.execute(query)
        count = result.scalar()

        return {
            "status": "success",
            "data": {"count": count},
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


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


async def get_farm_statistics(session: AsyncSession, owner_id: Optional[str] = None) -> Dict[str, Any]:
    try:
        count_query = select(func.count(Farm.id))

        if owner_id:
            count_query = count_query.filter(Farm.owner_id == owner_id)

        count_result = await session.execute(count_query)
        total_farms = count_result.scalar()

        if total_farms == 0:
            return {
                "status": "success",
                "data": {
                    'total_farms': 0,
                    'total_area_sqm': 0,
                    'total_area_hectares': 0,
                    'average_area_sqm': 0,
                    'smallest_farm_sqm': 0,
                    'largest_farm_sqm': 0
                },
                "error": None
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
            "status": "success",
            "data": {
                'total_farms': total_farms,
                'total_area_sqm': float(result.total_area or 0),
                'total_area_hectares': float(result.total_area or 0) / 10000,
                'average_area_sqm': float(result.avg_area or 0),
                'smallest_farm_sqm': float(result.min_area or 0),
                'largest_farm_sqm': float(result.max_area or 0)
            },
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }