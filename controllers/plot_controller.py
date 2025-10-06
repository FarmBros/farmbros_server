import json
from typing import Optional, Dict, Any, List

from shapely.geometry import shape, Polygon
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from aiocache import Cache, cached
from geoalchemy2 import Geography

from models.plot import Plot, PlotType
from models.farm import Farm
from models.plot_types import PLOT_TYPE_MODELS
from services.caching import *


async def create_plot_type_data(session: AsyncSession, plot_uuid: str, plot_type: str, plot_type_data: dict = None):
    """Create specific plot type data based on plot type"""
    if plot_type not in PLOT_TYPE_MODELS:
        return None
    
    plot_type_model = PLOT_TYPE_MODELS[plot_type]
    
    # Create instance with basic fields
    type_data = plot_type_model(
        plot_id=plot_uuid,
        name=plot_type_data.get('name', '') if plot_type_data else '',
        notes=plot_type_data.get('notes', '') if plot_type_data else ''
    )
    
    # Set specific fields based on plot type and provided data
    if plot_type_data:
        for key, value in plot_type_data.items():
            if hasattr(type_data, key) and key not in ['plot_id', 'id', 'uuid', 'created_at', 'updated_at']:
                setattr(type_data, key, value)
    
    session.add(type_data)
    return type_data


async def get_plot_type_data(session: AsyncSession, plot_uuid: str, plot_type: str):
    """Get plot type data for a specific plot"""
    if plot_type not in PLOT_TYPE_MODELS:
        return None
    
    plot_type_model = PLOT_TYPE_MODELS[plot_type]
    
    query = select(plot_type_model).filter(plot_type_model.plot_id == plot_uuid)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def delete_plot_type_data(session: AsyncSession, plot_uuid: str, plot_type: str):
    """Delete plot type data for a specific plot"""
    if plot_type not in PLOT_TYPE_MODELS:
        return
    
    plot_type_model = PLOT_TYPE_MODELS[plot_type]
    
    query = select(plot_type_model).filter(plot_type_model.plot_id == plot_uuid)
    result = await session.execute(query)
    type_data = result.scalar_one_or_none()
    
    if type_data:
        await session.delete(type_data)


async def attach_plot_type_data_to_plots(session: AsyncSession, plots, include_geojson=True):
    """Helper function to attach plot type data to a list of plots"""
    plot_dicts = []
    for plot in plots:
        if include_geojson:
            plot.boundary_geojson = await get_plot_boundary_as_geojson(session, plot.id)
            plot.centroid_geojson = await get_plot_centroid_as_geojson(session, plot.id)

        plot_dict = plot.to_dict(include_geometry=include_geojson)
        
        # Get plot type data manually
        if plot.plot_type:
            type_data = await get_plot_type_data(session, plot.uuid, plot.plot_type.value)
            if type_data:
                plot_dict['plot_type_data'] = type_data.to_dict()
        
        plot_dicts.append(plot_dict)
    
    return plot_dicts


async def create_plot(
        session: AsyncSession,
        data: Dict[str, Any],
        user: Dict[str, Any]
) -> Dict[str, Any]:
    try:
        name = data.get("name")
        farm_id = data.get("farm_id")
        plot_number = data.get("plot_number")
        plot_type_str = data.get("plot_type", "field")
        notes = data.get("notes", "")
        boundary_geojson = data["geojson"]
        plot_type_data = data.get("plot_type_data")

        # Validate farm exists and user has access
        farm_query = select(Farm).filter(Farm.uuid == farm_id, Farm.owner_id == user["uuid"])
        farm_result = await session.execute(farm_query)
        farm = farm_result.scalar_one_or_none()
        
        if not farm:
            return {
                "status": "error",
                "message": "Farm not found or access denied",
            }

        # Validate plot type
        try:
            plot_type = PlotType(plot_type_str)
        except ValueError:
            return {
                "status": "error",
                "message": f"Invalid plot type: {plot_type_str}",
            }

        boundary_shape = shape(boundary_geojson)

        if not isinstance(boundary_shape, Polygon):
            return {
                "status": "error",
                "message": "Invalid shape - must be a polygon",
            }

        # Check if plot boundary is within farm boundary
        plot_geometry = func.ST_GeomFromText(boundary_shape.wkt, 4326)
        
        try:
            # Use ST_Within with both geometries converted to the same coordinate system
            # Convert farm geography to geometry for comparison
            boundary_check_query = select(
                func.ST_Within(
                    plot_geometry,
                    func.ST_GeomFromText(func.ST_AsText(Farm.boundary), 4326)
                )
            ).filter(Farm.id == farm.id)
            
            boundary_check_result = await session.execute(boundary_check_query)
            is_within_farm = boundary_check_result.scalar()
            
            if not is_within_farm:
                return {
                    "status": "error",
                    "message": "Plot boundary must be within the farm boundary",
                }
        except Exception as e:
            # If boundary check fails, log and allow creation for now
            print(f"Boundary validation failed: {e}")
            # Uncomment next line to enforce boundary validation
            # return {"status": "error", "message": f"Boundary validation error: {e}"}

        centroid = boundary_shape.centroid

        plot = Plot(
            name=name,
            farm_id=farm.id,
            plot_type=plot_type,
            plot_number=plot_number,
            notes=notes
        )

        plot.boundary = plot_geometry
        plot.centroid = func.ST_GeomFromText(centroid.wkt, 4326)

        session.add(plot)
        await session.flush()

        # Calculate area
        area_result = await session.execute(
            select(func.ST_Area(Plot.boundary)).filter(Plot.id == plot.id)
        )
        area_query = area_result.scalar()
        plot.area_sqm = area_query

        await session.commit()
        await session.refresh(plot)

        # Create plot type specific data if provided
        if plot_type_data:
            type_data = await create_plot_type_data(session, plot.uuid, plot_type_str, plot_type_data)
            await session.commit()
            await session.refresh(plot)  # Refresh to get the relationship data

        # Invalidate relevant caches
        if not await invalidate_patterns(user['uuid'], [
            f"plots:farm:{farm.uuid}:*",
            f"plots:user:*",
            "plots:count",
            "dashboard",
            "stats:*"
        ]): 
            return {"status": "error", "message": "Could not invalidate plot cache"}

        # Get plot type data manually
        plot_dict = plot.to_dict()
        if plot.plot_type:
            type_data = await get_plot_type_data(session, plot.uuid, plot.plot_type.value)
            if type_data:
                plot_dict['plot_type_data'] = type_data.to_dict()

        return {
            "status": "success",
            "data": plot_dict,
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_plot(
        session: AsyncSession,
        user: Dict[str, Any],
        plot_id: str,
        include_geojson: bool = True
) -> Dict[str, Any]:
    try:
        # Join with farm to check ownership
        query = select(Plot).join(Farm).filter(
            Plot.uuid == plot_id,
            Farm.owner_id == user["uuid"]
        )

        result = await session.execute(query)
        plot = result.scalar_one_or_none()

        if not plot:
            return {
                "status": "error",
                "data": None,
                "error": "Plot not found"
            }

        if include_geojson:
            plot.boundary_geojson = await get_plot_boundary_as_geojson(session, plot.id)
            plot.centroid_geojson = await get_plot_centroid_as_geojson(session, plot.id)

        # Get plot type data manually
        plot_dict = plot.to_dict(include_geometry=include_geojson)
        if plot.plot_type:
            type_data = await get_plot_type_data(session, plot.uuid, plot.plot_type.value)
            if type_data:
                plot_dict['plot_type_data'] = type_data.to_dict()

        return {
            "status": "success",
            "data": plot_dict,
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


@cached(cache=Cache.REDIS, ttl=86400,
    key_builder=lambda f, session, farm_id, include_geojson=True, skip=0, limit=100:
    gen_user_key("system", "plots", "farm", farm_id,
                  gen_query_hash({"skip": skip, "limit": limit, "include_geojson": include_geojson}))
)
async def get_plots_by_farm(
        session: AsyncSession,
        farm_id: str,
        include_geojson: bool = True,
        skip: int = 0,
        limit: int = 100
) -> Dict[str, Any]:
    try:
        # Get farm first to validate it exists
        farm_query = select(Farm).filter(Farm.uuid == farm_id)
        farm_result = await session.execute(farm_query)
        farm = farm_result.scalar_one_or_none()
        
        if not farm:
            return {
                "status": "error",
                "data": None,
                "error": "Farm not found"
            }

        query = select(Plot).filter(
            Plot.farm_id == farm.id
        ).offset(skip).limit(limit)

        result = await session.execute(query)
        plots = result.scalars().all()

        plot_dicts = await attach_plot_type_data_to_plots(session, plots, include_geojson)

        return {
            "status": "success",
            "data": plot_dicts,
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


@cached(cache=Cache.REDIS, ttl=86400,
    key_builder=lambda f, session, user_id, include_geojson=True, skip=0, limit=100:
    gen_user_key(user_id, "plots", "user_list",
                  gen_query_hash({"skip": skip, "limit": limit, "include_geojson": include_geojson}))
)
async def get_plots_by_user(
        session: AsyncSession,
        user_id: str,
        include_geojson: bool = True,
        skip: int = 0,
        limit: int = 100
) -> Dict[str, Any]:
    try:
        query = select(Plot).join(Farm).filter(
            Farm.owner_id == user_id
        ).offset(skip).limit(limit)

        result = await session.execute(query)
        plots = result.scalars().all()

        plot_dicts = await attach_plot_type_data_to_plots(session, plots, include_geojson)

        return {
            "status": "success",
            "data": plot_dicts,
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def update_plot(
        session: AsyncSession,
        plot_id: str,
        user: Dict[str, Any],
        name: Optional[str] = None,
        plot_number: Optional[str] = None,
        plot_type: Optional[str] = None,
        notes: Optional[str] = None,
        boundary_geojson: Optional[Dict[str, Any]] = None,
        plot_type_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    try:
        # Join with farm to check ownership
        query = select(Plot).join(Farm).filter(
            Plot.uuid == plot_id,
            Farm.owner_id == user["uuid"]
        )
        result = await session.execute(query)
        plot = result.scalar_one_or_none()

        if not plot:
            return {
                "status": "error",
                "data": None,
                "error": "Plot not found"
            }

        if name is not None:
            plot.name = name

        if plot_number is not None:
            plot.plot_number = plot_number

        if plot_type is not None:
            try:
                plot.plot_type = PlotType(plot_type)
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Invalid plot type: {plot_type}"
                }

        if notes is not None:
            plot.notes = notes

        if boundary_geojson is not None:
            boundary_shape = shape(boundary_geojson)

            if not isinstance(boundary_shape, Polygon):
                raise ValueError("Boundary must be a Polygon")

            # Check if updated plot boundary is within farm boundary
            plot_geometry = func.ST_GeomFromText(boundary_shape.wkt, 4326)
            
            try:
                boundary_check_query = select(
                    func.ST_Within(
                        plot_geometry,
                        func.ST_GeomFromText(func.ST_AsText(Farm.boundary), 4326)
                    )
                ).filter(Farm.id == plot.farm_id)
                
                boundary_check_result = await session.execute(boundary_check_query)
                is_within_farm = boundary_check_result.scalar()
                
                if not is_within_farm:
                    return {
                        "status": "error",
                        "data": None,
                        "error": "Updated plot boundary must be within the farm boundary"
                    }
            except Exception as e:
                print(f"Update boundary validation failed: {e}")
                # Uncomment next line to enforce boundary validation
                # return {"status": "error", "message": f"Boundary validation error: {e}"}

            plot.boundary = plot_geometry
            plot.centroid = func.ST_GeomFromText(boundary_shape.centroid.wkt, 4326)

            await session.flush()

            # Recalculate area
            area_result = await session.execute(
                select(func.ST_Area(Plot.boundary)).filter(Plot.id == plot.id)
            )
            area_query = area_result.scalar()
            plot.area_sqm = area_query

        # Handle plot type data updates
        if plot_type_data is not None:
            # If plot type changed, we might need to create new type data
            current_plot_type = plot.plot_type.value if plot.plot_type else "field"
            target_plot_type = plot_type if plot_type else current_plot_type
            
            # Delete existing plot type data if it exists
            await delete_plot_type_data(session, plot.uuid, current_plot_type)
            await session.flush()
            
            # Create new plot type data
            if plot_type_data:
                await create_plot_type_data(session, plot.uuid, target_plot_type, plot_type_data)

        plot.update_timestamp()

        await session.commit()
        await session.refresh(plot)

        # Get farm for cache invalidation
        farm_query = select(Farm).filter(Farm.id == plot.farm_id)
        farm_result = await session.execute(farm_query)
        farm = farm_result.scalar_one()

        # Invalidate relevant caches
        await invalidate_patterns(user['uuid'], [
            f"plots:farm:{farm.uuid}:*",
            f"plots:user:*",
            "plots:count",
            "dashboard",
            "stats:*"
        ])

        plot.boundary_geojson = await get_plot_boundary_as_geojson(session, plot.id)
        plot.centroid_geojson = await get_plot_centroid_as_geojson(session, plot.id)

        # Get plot type data manually
        plot_dict = plot.to_dict(include_geometry=True)
        if plot.plot_type:
            type_data = await get_plot_type_data(session, plot.uuid, plot.plot_type.value)
            if type_data:
                plot_dict['plot_type_data'] = type_data.to_dict()

        return {
            "status": "success",
            "data": plot_dict,
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def delete_plot(
        session: AsyncSession, 
        plot_id: str,
        user: Dict[str, Any]
) -> Dict[str, Any]:
    try:
        # Join with farm to check ownership
        query = select(Plot).join(Farm).filter(
            Plot.uuid == plot_id,
            Farm.owner_id == user["uuid"]
        )
        result = await session.execute(query)
        plot = result.scalar_one_or_none()

        if not plot:
            return {
                "status": "error",
                "data": None,
                "error": "Plot not found"
            }

        # Get farm for cache invalidation
        farm_query = select(Farm).filter(Farm.id == plot.farm_id)
        farm_result = await session.execute(farm_query)
        farm = farm_result.scalar_one()

        await session.delete(plot)
        await session.commit()

        # Invalidate relevant caches
        await invalidate_patterns(user['uuid'], [
            f"plots:farm:{farm.uuid}:*",
            f"plots:user:*",
            "plots:count",
            "dashboard",
            "stats:*"
        ])
        
        return {
            "status": "success",
            "data": {"deleted": True, "plot_id": plot_id},
            "error": None
        }
        
    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_plots_by_type(
        session: AsyncSession,
        user_id: str,
        plot_type: str,
        include_geojson: bool = True,
        skip: int = 0,
        limit: int = 100
) -> Dict[str, Any]:
    try:
        # Validate plot type
        try:
            plot_type_enum = PlotType(plot_type)
        except ValueError:
            return {
                "status": "error",
                "data": None,
                "error": f"Invalid plot type: {plot_type}"
            }

        query = select(Plot).join(Farm).filter(
            Farm.owner_id == user_id,
            Plot.plot_type == plot_type_enum
        ).offset(skip).limit(limit)

        result = await session.execute(query)
        plots = result.scalars().all()

        plot_dicts = await attach_plot_type_data_to_plots(session, plots, include_geojson)

        return {
            "status": "success",
            "data": plot_dicts,
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def count_plots_by_farm(session: AsyncSession, farm_id: str) -> Dict[str, Any]:
    try:
        # Get farm first to validate it exists
        farm_query = select(Farm).filter(Farm.uuid == farm_id)
        farm_result = await session.execute(farm_query)
        farm = farm_result.scalar_one_or_none()
        
        if not farm:
            return {
                "status": "error",
                "data": None,
                "error": "Farm not found"
            }

        query = select(func.count(Plot.id)).filter(Plot.farm_id == farm.id)
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


async def calculate_total_plot_area_by_farm(session: AsyncSession, farm_id: str) -> Dict[str, Any]:
    try:
        # Get farm first to validate it exists
        farm_query = select(Farm).filter(Farm.uuid == farm_id)
        farm_result = await session.execute(farm_query)
        farm = farm_result.scalar_one_or_none()
        
        if not farm:
            return {
                "status": "error",
                "data": None,
                "error": "Farm not found"
            }

        query = select(func.sum(Plot.area_sqm)).filter(Plot.farm_id == farm.id)
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


async def get_plot_statistics(
        session: AsyncSession, 
        user_id: Optional[str] = None,
        farm_id: Optional[str] = None
) -> Dict[str, Any]:
    try:
        count_query = select(func.count(Plot.id))

        if farm_id:
            # Get farm first to validate it exists
            farm_query = select(Farm).filter(Farm.uuid == farm_id)
            farm_result = await session.execute(farm_query)
            farm = farm_result.scalar_one_or_none()
            
            if not farm:
                return {
                    "status": "error",
                    "data": None,
                    "error": "Farm not found"
                }
            count_query = count_query.filter(Plot.farm_id == farm.id)
        elif user_id:
            count_query = count_query.join(Farm).filter(Farm.owner_id == user_id)

        count_result = await session.execute(count_query)
        total_plots = count_result.scalar()

        if total_plots == 0:
            return {
                "status": "success",
                "data": {
                    'total_plots': 0,
                    'total_area_sqm': 0,
                    'total_area_hectares': 0,
                    'average_area_sqm': 0,
                    'smallest_plot_sqm': 0,
                    'largest_plot_sqm': 0
                },
                "error": None
            }

        stats_query = select(
            func.sum(Plot.area_sqm).label('total_area'),
            func.avg(Plot.area_sqm).label('avg_area'),
            func.min(Plot.area_sqm).label('min_area'),
            func.max(Plot.area_sqm).label('max_area')
        )

        if farm_id:
            stats_query = stats_query.filter(Plot.farm_id == farm.id)
        elif user_id:
            stats_query = stats_query.join(Farm).filter(Farm.owner_id == user_id)

        stats_result = await session.execute(stats_query)
        result = stats_result.first()

        return {
            "status": "success",
            "data": {
                'total_plots': total_plots,
                'total_area_sqm': float(result.total_area or 0),
                'total_area_hectares': float(result.total_area or 0) / 10000,
                'average_area_sqm': float(result.avg_area or 0),
                'smallest_plot_sqm': float(result.min_area or 0),
                'largest_plot_sqm': float(result.max_area or 0)
            },
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_plot_boundary_as_geojson(session: AsyncSession, plot_id: int) -> Optional[Dict]:
    query = select(func.ST_AsGeoJSON(Plot.boundary)).filter(Plot.id == plot_id)
    result = await session.execute(query)
    geojson = result.scalar()

    return json.loads(geojson) if geojson else None


async def get_plot_centroid_as_geojson(session: AsyncSession, plot_id: int) -> Optional[Dict]:
    query = select(func.ST_AsGeoJSON(Plot.centroid)).filter(Plot.id == plot_id)
    result = await session.execute(query)
    geojson = result.scalar()

    return json.loads(geojson) if geojson else None


def validate_plot_geojson_polygon(geojson_data: Dict[str, Any]) -> bool:
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