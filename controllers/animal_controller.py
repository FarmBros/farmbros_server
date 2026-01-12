from typing import Optional, Dict, Any
from datetime import date, datetime

from sqlalchemy import func, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from aiocache import Cache, cached

from models.animal import Animal
from models.animal_type import AnimalType
from models.farm import Farm
from models.plot import Plot
from models.user import User
from services.caching import *


async def create_animal(
        session: AsyncSession,
        user_uuid: str,
        data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a new animal entry"""
    try:
        # Validate required fields - keys are _id, values are UUIDs
        farm_uuid = data.get("farm_id")
        animal_type_uuid = data.get("animal_type_id")
        name = data.get("name")

        if not all([farm_uuid, animal_type_uuid, name]):
            return {
                "status": "error",
                "data": None,
                "error": "farm_id, animal_type_id, and name are required"
            }

        # Verify that farm, animal_type, user exist and get their IDs
        farm_query = select(Farm).filter(Farm.uuid == farm_uuid)
        farm_result = await session.execute(farm_query)
        farm = farm_result.scalar_one_or_none()
        if not farm:
            return {
                "status": "error",
                "data": None,
                "error": f"Farm with uuid {farm_uuid} not found"
            }

        animal_type_query = select(AnimalType).filter(AnimalType.uuid == animal_type_uuid)
        animal_type_result = await session.execute(animal_type_query)
        animal_type = animal_type_result.scalar_one_or_none()
        if not animal_type:
            return {
                "status": "error",
                "data": None,
                "error": f"Animal type with uuid {animal_type_uuid} not found"
            }

        # Plot is optional
        plot = None
        plot_uuid = data.get("plot_id")
        if plot_uuid:
            plot_query = select(Plot).filter(Plot.uuid == plot_uuid)
            plot_result = await session.execute(plot_query)
            plot = plot_result.scalar_one_or_none()
            if not plot:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Plot with uuid {plot_uuid} not found"
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

        # Parse dates if provided (format: DD-MM-YYYY)
        birth_date = None
        if data.get("birth_date"):
            try:
                birth_date = datetime.strptime(data["birth_date"], "%d-%m-%Y").date()
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": "Invalid birth_date format. Use DD-MM-YYYY"
                }

        brought_in_date = None
        if data.get("brought_in_date"):
            try:
                brought_in_date = datetime.strptime(data["brought_in_date"], "%d-%m-%Y").date()
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": "Invalid brought_in_date format. Use DD-MM-YYYY"
                }

        weaning_date = None
        if data.get("weaning_date"):
            try:
                weaning_date = datetime.strptime(data["weaning_date"], "%d-%m-%Y").date()
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": "Invalid weaning_date format. Use DD-MM-YYYY"
                }

        removal_date = None
        if data.get("removal_date"):
            try:
                removal_date = datetime.strptime(data["removal_date"], "%d-%m-%Y").date()
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": "Invalid removal_date format. Use DD-MM-YYYY"
                }

        # Validate is_batch and batch_count
        is_batch = data.get("is_batch", False)
        batch_count = data.get("batch_count")

        if is_batch and not batch_count:
            return {
                "status": "error",
                "data": None,
                "error": "batch_count is required when is_batch is True"
            }

        animal = Animal(
            farm_id=farm.id,
            animal_type_id=animal_type.id,
            user_id=user.id,
            name=name,
            plot_id=plot.id if plot else None,
            identifier=data.get("identifier"),
            color=data.get("color"),
            use=data.get("use"),
            is_batch=is_batch,
            batch_count=batch_count,
            birth_date=birth_date,
            brought_in_date=brought_in_date,
            weaning_date=weaning_date,
            removal_date=removal_date,
            parents_id=data.get("parents_id"),
            notes=data.get("notes")
        )

        session.add(animal)
        await session.commit()
        await session.refresh(animal, ['farm', 'plot', 'animal_type', 'user'])

        # Invalidate relevant caches
        await invalidate_patterns("system", [
            "animals:*",
            f"farm:{farm.id}:*",
            f"user:{user.id}:*",
            "dashboard",
            "stats:*"
        ])

        return {
            "status": "success",
            "data": animal.to_dict(),
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_animal(
        session: AsyncSession,
        user_uuid: str,
        animal_uuid: str
) -> Dict[str, Any]:
    """Get a single animal by UUID (only if it belongs to the authenticated user)"""
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

        query = select(Animal).options(
            selectinload(Animal.farm),
            selectinload(Animal.plot),
            selectinload(Animal.animal_type),
            selectinload(Animal.user)
        ).filter(
            Animal.uuid == animal_uuid,
            Animal.user_id == user.id
        )
        result = await session.execute(query)
        animal = result.scalar_one_or_none()

        if not animal:
            return {
                "status": "error",
                "data": None,
                "error": f"Animal with uuid {animal_uuid} not found or access denied"
            }

        return {
            "status": "success",
            "data": animal.to_dict(),
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


@cached(cache=Cache.REDIS, ttl=600,
    key_builder=lambda f, session, user_uuid, skip=0, limit=100, farm_id=None, animal_type_id=None, is_active=None:
    gen_user_key(user_uuid, "animals", "list",
                  gen_query_hash({"skip": skip, "limit": limit, "farm_id": farm_id,
                                 "animal_type_id": animal_type_id, "is_active": is_active}))
)
async def get_all_animals(
        session: AsyncSession,
        user_uuid: str,
        skip: int = 0,
        limit: int = 100,
        farm_id: Optional[str] = None,
        animal_type_id: Optional[str] = None,
        is_active: Optional[bool] = None
) -> Dict[str, Any]:
    """Get all animals for a user with optional filtering"""
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

        query = select(Animal).options(
            selectinload(Animal.farm),
            selectinload(Animal.plot),
            selectinload(Animal.animal_type),
            selectinload(Animal.user)
        ).filter(Animal.user_id == user.id)

        # Apply filters
        if farm_id:
            farm_query = select(Farm).filter(Farm.uuid == farm_id)
            farm_result = await session.execute(farm_query)
            farm = farm_result.scalar_one_or_none()
            if farm:
                query = query.filter(Animal.farm_id == farm.id)
            else:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Farm with uuid {farm_id} not found"
                }

        if animal_type_id:
            animal_type_query = select(AnimalType).filter(AnimalType.uuid == animal_type_id)
            animal_type_result = await session.execute(animal_type_query)
            animal_type = animal_type_result.scalar_one_or_none()
            if animal_type:
                query = query.filter(Animal.animal_type_id == animal_type.id)
            else:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Animal type with uuid {animal_type_id} not found"
                }

        if is_active is not None:
            if is_active:
                query = query.filter(Animal.removal_date.is_(None))
            else:
                query = query.filter(Animal.removal_date.isnot(None))

        # Add pagination
        query = query.offset(skip).limit(limit)

        result = await session.execute(query)
        animals = result.scalars().all()

        animal_dicts = [animal.to_dict() for animal in animals]

        return {
            "status": "success",
            "data": animal_dicts,
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def update_animal(
        session: AsyncSession,
        user_uuid: str,
        animal_uuid: str,
        data: Dict[str, Any]
) -> Dict[str, Any]:
    """Update an animal entry"""
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

        query = select(Animal).filter(
            Animal.uuid == animal_uuid,
            Animal.user_id == user.id
        )
        result = await session.execute(query)
        animal = result.scalar_one_or_none()

        if not animal:
            return {
                "status": "error",
                "data": None,
                "error": "Animal not found or access denied"
            }

        # Update foreign key relationships if provided
        if "farm_id" in data and data["farm_id"]:
            farm_query = select(Farm).filter(Farm.uuid == data["farm_id"])
            farm_result = await session.execute(farm_query)
            farm = farm_result.scalar_one_or_none()
            if not farm:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Farm with uuid {data['farm_id']} not found"
                }
            animal.farm_id = farm.id

        if "plot_id" in data:
            if data["plot_id"]:
                plot_query = select(Plot).filter(Plot.uuid == data["plot_id"])
                plot_result = await session.execute(plot_query)
                plot = plot_result.scalar_one_or_none()
                if not plot:
                    return {
                        "status": "error",
                        "data": None,
                        "error": f"Plot with uuid {data['plot_id']} not found"
                    }
                animal.plot_id = plot.id
            else:
                animal.plot_id = None

        if "animal_type_id" in data and data["animal_type_id"]:
            animal_type_query = select(AnimalType).filter(AnimalType.uuid == data["animal_type_id"])
            animal_type_result = await session.execute(animal_type_query)
            animal_type = animal_type_result.scalar_one_or_none()
            if not animal_type:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Animal type with uuid {data['animal_type_id']} not found"
                }
            animal.animal_type_id = animal_type.id

        # Update basic fields
        if "name" in data:
            animal.name = data["name"]

        if "identifier" in data:
            animal.identifier = data["identifier"]

        if "color" in data:
            animal.color = data["color"]

        if "use" in data:
            animal.use = data["use"]

        if "is_batch" in data:
            animal.is_batch = data["is_batch"]

        if "batch_count" in data:
            animal.batch_count = data["batch_count"]

        if "parents_id" in data:
            animal.parents_id = data["parents_id"]

        if "notes" in data:
            animal.notes = data["notes"]

        # Update date fields (format: DD-MM-YYYY)
        date_fields = {
            "birth_date": "birth_date",
            "brought_in_date": "brought_in_date",
            "weaning_date": "weaning_date",
            "removal_date": "removal_date"
        }

        for field_key, field_name in date_fields.items():
            if field_key in data:
                if data[field_key]:
                    try:
                        setattr(animal, field_name, datetime.strptime(data[field_key], "%d-%m-%Y").date())
                    except ValueError:
                        return {
                            "status": "error",
                            "data": None,
                            "error": f"Invalid {field_key} format. Use DD-MM-YYYY"
                        }
                else:
                    setattr(animal, field_name, None)

        animal.update_timestamp()

        await session.commit()
        await session.refresh(animal, ['farm', 'plot', 'animal_type', 'user'])

        # Invalidate relevant caches
        await invalidate_patterns("system", [
            "animals:*",
            f"farm:{animal.farm_id}:*",
            f"user:{user.id}:*",
            "dashboard",
            "stats:*"
        ])

        return {
            "status": "success",
            "data": animal.to_dict(),
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def delete_animal(
        session: AsyncSession,
        user_uuid: str,
        animal_uuid: str
) -> Dict[str, Any]:
    """Delete an animal entry"""
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

        query = select(Animal).filter(
            Animal.uuid == animal_uuid,
            Animal.user_id == user.id
        )
        result = await session.execute(query)
        animal = result.scalar_one_or_none()

        if not animal:
            return {
                "status": "error",
                "data": None,
                "error": "Animal not found or access denied"
            }

        farm_id = animal.farm_id

        await session.delete(animal)
        await session.commit()

        # Invalidate relevant caches
        await invalidate_patterns("system", [
            "animals:*",
            f"farm:{farm_id}:*",
            f"user:{user.id}:*",
            "dashboard",
            "stats:*"
        ])

        return {
            "status": "success",
            "data": {"deleted": True, "animal_id": animal_uuid},
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def search_animals(
        session: AsyncSession,
        user_uuid: str,
        search_term: str,
        skip: int = 0,
        limit: int = 50
) -> Dict[str, Any]:
    """Search animals by name or identifier"""
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

        search_pattern = f"%{search_term}%"

        query = select(Animal).options(
            selectinload(Animal.farm),
            selectinload(Animal.plot),
            selectinload(Animal.animal_type),
            selectinload(Animal.user)
        ).filter(
            Animal.user_id == user.id,
            or_(
                Animal.name.ilike(search_pattern),
                Animal.identifier.ilike(search_pattern),
                Animal.color.ilike(search_pattern)
            )
        ).offset(skip).limit(limit)

        result = await session.execute(query)
        animals = result.scalars().all()

        animal_dicts = [animal.to_dict() for animal in animals]

        return {
            "status": "success",
            "data": animal_dicts,
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def count_animals(
        session: AsyncSession,
        user_uuid: str,
        farm_id: Optional[str] = None,
        animal_type_id: Optional[str] = None,
        is_active: Optional[bool] = None
) -> Dict[str, Any]:
    """Count total animals for a user with optional filtering"""
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

        query = select(func.count(Animal.id)).filter(Animal.user_id == user.id)

        # Apply filters
        if farm_id:
            farm_query = select(Farm).filter(Farm.uuid == farm_id)
            farm_result = await session.execute(farm_query)
            farm = farm_result.scalar_one_or_none()
            if farm:
                query = query.filter(Animal.farm_id == farm.id)

        if animal_type_id:
            animal_type_query = select(AnimalType).filter(AnimalType.uuid == animal_type_id)
            animal_type_result = await session.execute(animal_type_query)
            animal_type = animal_type_result.scalar_one_or_none()
            if animal_type:
                query = query.filter(Animal.animal_type_id == animal_type.id)

        if is_active is not None:
            if is_active:
                query = query.filter(Animal.removal_date.is_(None))
            else:
                query = query.filter(Animal.removal_date.isnot(None))

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


async def get_animal_statistics(
        session: AsyncSession,
        user_uuid: str,
        farm_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get statistics about animals for a user"""
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

        # Base query filter
        base_filter = [Animal.user_id == user.id]

        # Add farm filter if provided
        if farm_id:
            farm_query = select(Farm).filter(Farm.uuid == farm_id)
            farm_result = await session.execute(farm_query)
            farm = farm_result.scalar_one_or_none()
            if farm:
                base_filter.append(Animal.farm_id == farm.id)

        # Count total animals
        total_query = select(func.count(Animal.id)).filter(and_(*base_filter))
        total_result = await session.execute(total_query)
        total_animals = total_result.scalar()

        # Count active animals (not removed)
        active_query = select(func.count(Animal.id)).filter(
            and_(*base_filter),
            Animal.removal_date.is_(None)
        )
        active_result = await session.execute(active_query)
        active_animals = active_result.scalar()

        # Count by animal type
        type_query = select(
            AnimalType.breed,
            func.count(Animal.id).label('count')
        ).join(Animal, Animal.animal_type_id == AnimalType.id).filter(
            and_(*base_filter)
        ).group_by(AnimalType.breed)
        type_result = await session.execute(type_query)
        by_type = {row.breed: row.count for row in type_result}

        # Count batches vs individuals
        batch_query = select(func.count(Animal.id)).filter(
            and_(*base_filter),
            Animal.is_batch == True
        )
        batch_result = await session.execute(batch_query)
        batch_count = batch_result.scalar()

        individual_count = total_animals - batch_count

        return {
            "status": "success",
            "data": {
                "total_animals": total_animals,
                "active_animals": active_animals,
                "removed_animals": total_animals - active_animals,
                "by_type": by_type,
                "batches": batch_count,
                "individuals": individual_count
            },
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }
