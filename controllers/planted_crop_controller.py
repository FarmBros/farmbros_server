from typing import Optional, Dict, Any, List
from datetime import datetime

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from aiocache import Cache, cached

from models.planted_crop import PlantedCrop
from models.crop import Crop
from models.plot import Plot, PlotType
from models.user import User
from services.caching import *


async def create_planted_crop(
        session: AsyncSession,
        user_uuid: str,
        data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a new planted crop entry"""
    try:
        # Validate required fields - keys are _id, values are UUIDs
        crop_uuid = data.get("crop_id")
        plot_uuid = data.get("plot_id")

        if not all([crop_uuid, plot_uuid]):
            return {
                "status": "error",
                "data": None,
                "error": "crop_id and plot_id are required"
            }

        # Verify that crop, plot, and user exist and get their IDs
        crop_query = select(Crop).filter(Crop.uuid == crop_uuid)
        crop_result = await session.execute(crop_query)
        crop = crop_result.scalar_one_or_none()
        if not crop:
            return {
                "status": "error",
                "data": None,
                "error": f"Crop with uuid {crop_uuid} not found"
            }

        plot_query = select(Plot).filter(Plot.uuid == plot_uuid)
        plot_result = await session.execute(plot_query)
        plot = plot_result.scalar_one_or_none()
        if not plot:
            return {
                "status": "error",
                "data": None,
                "error": f"Plot with uuid {plot_uuid} not found"
            }

        # Check if plot type allows crop planting
        allowed_plot_types = [PlotType.FIELD, PlotType.PASTURE, PlotType.NATURAL_AREA, PlotType.GREEN_HOUSE]
        if plot.plot_type not in allowed_plot_types:
            return {
                "status": "error",
                "data": None,
                "error": f"Cannot plant a crop in a {plot.plot_type.value} plot type"
            }

        user_query = select(User).filter(User.uuid == user_uuid)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()
        if not user:
            return {
                "status": "error",
                "data": None,
                "error": f"User with uuid {user_uuid} not found"
            }

        # Parse dates if provided - remove timezone info for database compatibility
        germination_date = None
        if data.get("germination_date"):
            try:
                dt = datetime.fromisoformat(data["germination_date"].replace('Z', '+00:00'))
                germination_date = dt.replace(tzinfo=None)  # Remove timezone info
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": "Invalid germination_date format"
                }

        transplant_date = None
        if data.get("transplant_date"):
            try:
                dt = datetime.fromisoformat(data["transplant_date"].replace('Z', '+00:00'))
                transplant_date = dt.replace(tzinfo=None)  # Remove timezone info
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": "Invalid transplant_date format"
                }

        harvest_date = None
        if data.get("harvest_date"):
            try:
                dt = datetime.fromisoformat(data["harvest_date"].replace('Z', '+00:00'))
                harvest_date = dt.replace(tzinfo=None)  # Remove timezone info
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": "Invalid harvest_date format"
                }

        planted_crop = PlantedCrop(
            crop_id=crop.id,
            plot_id=plot.id,
            user_id=user.id,
            planting_method=data.get("planting_method"),
            planting_spacing=data.get("planting_spacing"),
            germination_date=germination_date,
            transplant_date=transplant_date,
            seedling_age=data.get("seedling_age"),
            harvest_date=harvest_date,
            number_of_crops=data.get("number_of_crops"),
            estimated_yield=data.get("estimated_yield"),
            notes=data.get("notes")
        )

        session.add(planted_crop)
        await session.commit()
        await session.refresh(planted_crop, ['crop', 'plot', 'user'])

        # Invalidate relevant caches
        await invalidate_patterns("system", [
            "planted_crops:*",
            f"plot:{plot.id}:*",
            f"user:{user.id}:*",
            "dashboard",
            "stats:*"
        ])

        return {
            "status": "success",
            "data": planted_crop.to_dict(),
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_planted_crop(
        session: AsyncSession,
        user_uuid: str,
        planted_crop_uuid: str
) -> Dict[str, Any]:
    """Get a single planted crop by UUID (only if it belongs to the authenticated user)"""
    try:
        # Get user by UUID to get their ID for filtering
        user_query = select(User).filter(User.uuid == user_uuid)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            return {
                "status": "error",
                "data": None,
                "error": "User not found"
            }

        query = select(PlantedCrop).options(
            selectinload(PlantedCrop.crop),
            selectinload(PlantedCrop.plot),
            selectinload(PlantedCrop.user)
        ).filter(
            PlantedCrop.uuid == planted_crop_uuid,
            PlantedCrop.user_id == user.id
        )
        result = await session.execute(query)
        planted_crop = result.scalar_one_or_none()

        if not planted_crop:
            return {
                "status": "error",
                "data": None,
                "error": f"Planted crop with uuid {planted_crop_uuid} not found or access denied"
            }

        return {
            "status": "success",
            "data": planted_crop.to_dict(),
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_all_planted_crops(
        session: AsyncSession,
        user_uuid: str,
        skip: int = 0,
        limit: int = 100,
        plot_uuid: Optional[str] = None,
        crop_uuid: Optional[str] = None
) -> Dict[str, Any]:
    """Get all planted crops with optional filtering (filtered by authenticated user)"""
    try:
        # Get user by UUID
        user_query = select(User).filter(User.uuid == user_uuid)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            return {
                "status": "error",
                "data": None,
                "error": "User not found"
            }

        query = select(PlantedCrop).options(
            selectinload(PlantedCrop.crop),
            selectinload(PlantedCrop.plot),
            selectinload(PlantedCrop.user)
        )

        # Apply filters - always filter by user_id from token
        filters = [PlantedCrop.user_id == user.id]

        if plot_uuid:
            plot_query = select(Plot).filter(Plot.uuid == plot_uuid)
            plot_result = await session.execute(plot_query)
            plot = plot_result.scalar_one_or_none()
            if plot:
                filters.append(PlantedCrop.plot_id == plot.id)

        if crop_uuid:
            crop_query = select(Crop).filter(Crop.uuid == crop_uuid)
            crop_result = await session.execute(crop_query)
            crop = crop_result.scalar_one_or_none()
            if crop:
                filters.append(PlantedCrop.crop_id == crop.id)

        if filters:
            query = query.filter(and_(*filters))

        query = query.offset(skip).limit(limit).order_by(PlantedCrop.created_at.desc())

        result = await session.execute(query)
        planted_crops = result.scalars().all()

        return {
            "status": "success",
            "data": [pc.to_dict() for pc in planted_crops],
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def update_planted_crop(
        session: AsyncSession,
        user_uuid: str,
        planted_crop_uuid: str,
        data: Dict[str, Any]
) -> Dict[str, Any]:
    """Update a planted crop entry (only if it belongs to the authenticated user)"""
    try:
        # Get user by UUID
        user_query = select(User).filter(User.uuid == user_uuid)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            return {
                "status": "error",
                "data": None,
                "error": "User not found"
            }

        query = select(PlantedCrop).options(
            selectinload(PlantedCrop.crop),
            selectinload(PlantedCrop.plot),
            selectinload(PlantedCrop.user)
        ).filter(
            PlantedCrop.uuid == planted_crop_uuid,
            PlantedCrop.user_id == user.id
        )
        result = await session.execute(query)
        planted_crop = result.scalar_one_or_none()

        if not planted_crop:
            return {
                "status": "error",
                "data": None,
                "error": f"Planted crop with uuid {planted_crop_uuid} not found or access denied"
            }

        # Update fields if provided
        if "planting_method" in data:
            planted_crop.planting_method = data["planting_method"]
        if "planting_spacing" in data:
            planted_crop.planting_spacing = data["planting_spacing"]
        if "germination_date" in data:
            if data["germination_date"]:
                try:
                    dt = datetime.fromisoformat(
                        data["germination_date"].replace('Z', '+00:00')
                    )
                    planted_crop.germination_date = dt.replace(tzinfo=None)  # Remove timezone info
                except ValueError:
                    return {
                        "status": "error",
                        "data": None,
                        "error": "Invalid germination_date format"
                    }
            else:
                planted_crop.germination_date = None
        if "transplant_date" in data:
            if data["transplant_date"]:
                try:
                    dt = datetime.fromisoformat(
                        data["transplant_date"].replace('Z', '+00:00')
                    )
                    planted_crop.transplant_date = dt.replace(tzinfo=None)  # Remove timezone info
                except ValueError:
                    return {
                        "status": "error",
                        "data": None,
                        "error": "Invalid transplant_date format"
                    }
            else:
                planted_crop.transplant_date = None
        if "seedling_age" in data:
            planted_crop.seedling_age = data["seedling_age"]
        if "harvest_date" in data:
            if data["harvest_date"]:
                try:
                    dt = datetime.fromisoformat(
                        data["harvest_date"].replace('Z', '+00:00')
                    )
                    planted_crop.harvest_date = dt.replace(tzinfo=None)  # Remove timezone info
                except ValueError:
                    return {
                        "status": "error",
                        "data": None,
                        "error": "Invalid harvest_date format"
                    }
            else:
                planted_crop.harvest_date = None
        if "number_of_crops" in data:
            planted_crop.number_of_crops = data["number_of_crops"]
        if "estimated_yield" in data:
            planted_crop.estimated_yield = data["estimated_yield"]
        if "notes" in data:
            planted_crop.notes = data["notes"]

        planted_crop.update_timestamp()
        await session.commit()
        await session.refresh(planted_crop)

        # Invalidate relevant caches
        await invalidate_patterns("system", [
            "planted_crops:*",
            f"plot:{planted_crop.plot_id}:*",
            f"user:{planted_crop.user_id}:*",
            "dashboard",
            "stats:*"
        ])

        return {
            "status": "success",
            "data": planted_crop.to_dict(),
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def delete_planted_crop(
        session: AsyncSession,
        user_uuid: str,
        planted_crop_uuid: str
) -> Dict[str, Any]:
    """Delete a planted crop entry (only if it belongs to the authenticated user)"""
    try:
        # Get user by UUID
        user_query = select(User).filter(User.uuid == user_uuid)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            return {
                "status": "error",
                "data": None,
                "error": "User not found"
            }

        query = select(PlantedCrop).filter(
            PlantedCrop.uuid == planted_crop_uuid,
            PlantedCrop.user_id == user.id
        )
        result = await session.execute(query)
        planted_crop = result.scalar_one_or_none()

        if not planted_crop:
            return {
                "status": "error",
                "data": None,
                "error": f"Planted crop with uuid {planted_crop_uuid} not found or access denied"
            }

        plot_id = planted_crop.plot_id
        user_id = planted_crop.user_id

        await session.delete(planted_crop)
        await session.commit()

        # Invalidate relevant caches
        await invalidate_patterns("system", [
            "planted_crops:*",
            f"plot:{plot_id}:*",
            f"user:{user_id}:*",
            "dashboard",
            "stats:*"
        ])

        return {
            "status": "success",
            "data": {"message": f"Planted crop {planted_crop_uuid} deleted successfully"},
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def count_planted_crops(
        session: AsyncSession,
        user_uuid: str,
        plot_uuid: Optional[str] = None,
        crop_uuid: Optional[str] = None
) -> Dict[str, Any]:
    """Count planted crops with optional filtering (filtered by authenticated user)"""
    try:
        # Get user by UUID
        user_query = select(User).filter(User.uuid == user_uuid)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            return {
                "status": "error",
                "data": None,
                "error": "User not found"
            }

        query = select(func.count(PlantedCrop.id))

        # Apply filters - always filter by user_id from token
        filters = [PlantedCrop.user_id == user.id]

        if plot_uuid:
            plot_query = select(Plot).filter(Plot.uuid == plot_uuid)
            plot_result = await session.execute(plot_query)
            plot = plot_result.scalar_one_or_none()
            if plot:
                filters.append(PlantedCrop.plot_id == plot.id)

        if crop_uuid:
            crop_query = select(Crop).filter(Crop.uuid == crop_uuid)
            crop_result = await session.execute(crop_query)
            crop = crop_result.scalar_one_or_none()
            if crop:
                filters.append(PlantedCrop.crop_id == crop.id)

        if filters:
            query = query.filter(and_(*filters))

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


async def get_planted_crops_with_details(
        session: AsyncSession,
        user_uuid: str,
        skip: int = 0,
        limit: int = 100,
        plot_uuid: Optional[str] = None
) -> Dict[str, Any]:
    """Get planted crops with related crop, plot, and user details (filtered by authenticated user)"""
    try:
        # Get user by UUID
        user_query = select(User).filter(User.uuid == user_uuid)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            return {
                "status": "error",
                "data": None,
                "error": "User not found"
            }

        query = select(PlantedCrop).options(
            selectinload(PlantedCrop.crop),
            selectinload(PlantedCrop.plot),
            selectinload(PlantedCrop.user)
        )

        # Apply filters - always filter by user_id from token
        filters = [PlantedCrop.user_id == user.id]

        if plot_uuid:
            plot_query = select(Plot).filter(Plot.uuid == plot_uuid)
            plot_result = await session.execute(plot_query)
            plot = plot_result.scalar_one_or_none()
            if plot:
                filters.append(PlantedCrop.plot_id == plot.id)

        if filters:
            query = query.filter(and_(*filters))

        query = query.offset(skip).limit(limit).order_by(PlantedCrop.created_at.desc())

        result = await session.execute(query)
        planted_crops = result.scalars().all()

        data = []
        for pc in planted_crops:
            pc_dict = pc.to_dict()
            pc_dict['crop'] = pc.crop.to_dict() if pc.crop else None
            pc_dict['plot'] = pc.plot.to_dict() if pc.plot else None
            pc_dict['user'] = {
                'id': pc.user.id,
                'username': pc.user.username,
                'email': pc.user.email
            } if pc.user else None
            data.append(pc_dict)

        return {
            "status": "success",
            "data": data,
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_planted_crop_statistics(
        session: AsyncSession,
        user_uuid: str
) -> Dict[str, Any]:
    """Get statistics about planted crops for authenticated user"""
    try:
        # Get user by UUID
        user_query = select(User).filter(User.uuid == user_uuid)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            return {
                "status": "error",
                "data": None,
                "error": "User not found"
            }

        # Base query - always filter by user_id from token
        base_filter = PlantedCrop.user_id == user.id

        # Total count
        total_query = select(func.count(PlantedCrop.id)).filter(base_filter)
        total_result = await session.execute(total_query)
        total_count = total_result.scalar()

        # Count by plot - return UUIDs instead of integer IDs
        by_plot_query = select(
            Plot.uuid,
            func.count(PlantedCrop.id).label('count')
        ).join(Plot, PlantedCrop.plot_id == Plot.id).filter(base_filter).group_by(Plot.uuid)
        by_plot_result = await session.execute(by_plot_query)
        by_plot = [{"plot_id": row[0], "count": row[1]} for row in by_plot_result]

        # Count by crop - return UUIDs instead of integer IDs
        by_crop_query = select(
            Crop.uuid,
            func.count(PlantedCrop.id).label('count')
        ).join(Crop, PlantedCrop.crop_id == Crop.id).filter(base_filter).group_by(Crop.uuid)
        by_crop_result = await session.execute(by_crop_query)
        by_crop = [{"crop_id": row[0], "count": row[1]} for row in by_crop_result]

        # Total estimated yield
        yield_query = select(func.sum(PlantedCrop.estimated_yield)).filter(base_filter)
        yield_result = await session.execute(yield_query)
        total_yield = yield_result.scalar() or 0

        # Total plants
        plants_query = select(func.sum(PlantedCrop.number_of_crops)).filter(base_filter)
        plants_result = await session.execute(plants_query)
        total_plants = plants_result.scalar() or 0

        return {
            "status": "success",
            "data": {
                "total_planted_crops": total_count,
                "by_plot": by_plot,
                "by_crop": by_crop,
                "total_estimated_yield_kg": float(total_yield),
                "total_plants": int(total_plants)
            },
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }
