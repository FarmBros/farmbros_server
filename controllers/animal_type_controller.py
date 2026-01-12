from typing import Optional, Dict, Any
import hashlib

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from aiocache import Cache, cached

from models.animal_type import AnimalType, AnimalSex, AnimalCategory
from services.caching import *


async def create_animal_type(
        session: AsyncSession,
        data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a new animal type entry"""
    try:
        breed = data.get("breed")
        category_str = data.get("category")

        if not breed or not category_str:
            return {
                "status": "error",
                "data": None,
                "error": "breed and category are required"
            }

        # Parse category enum
        try:
            category = AnimalCategory(category_str)
        except ValueError:
            return {
                "status": "error",
                "data": None,
                "error": f"Invalid category: {category_str}. Valid options: {[e.value for e in AnimalCategory]}"
            }

        # Parse sex enum if provided
        sex = None
        if data.get("sex"):
            try:
                sex = AnimalSex(data["sex"])
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Invalid sex: {data['sex']}. Valid options: {[e.value for e in AnimalSex]}"
                }

        animal_type = AnimalType(
            breed=breed,
            category=category,
            species=data.get("species"),
            sex=sex,
            category_type=data.get("category_type"),
            puberty_age=data.get("puberty_age"),
            estrus_cycle_type=data.get("estrus_cycle_type"),
            estrus_cycle_length=data.get("estrus_cycle_length"),
            estrus_duration=data.get("estrus_duration"),
            best_breeding_time=data.get("best_breeding_time"),
            heat_signs=data.get("heat_signs"),
            age_at_first_egg=data.get("age_at_first_egg"),
            days_to_breed=data.get("days_to_breed"),
            days_to_market=data.get("days_to_market"),
            notes=data.get("notes")
        )

        session.add(animal_type)
        await session.commit()
        await session.refresh(animal_type)

        # Invalidate relevant caches
        await invalidate_patterns("system", [
            "animal_types:*",
            "dashboard",
            "stats:*"
        ])

        return {
            "status": "success",
            "data": animal_type.to_dict(),
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_animal_type(
        session: AsyncSession,
        animal_type_id: str
) -> Dict[str, Any]:
    """Get a single animal type by UUID"""
    try:
        query = select(AnimalType).filter(AnimalType.uuid == animal_type_id)
        result = await session.execute(query)
        animal_type = result.scalar_one_or_none()

        if not animal_type:
            return {
                "status": "error",
                "data": None,
                "error": "Animal type not found"
            }

        return {
            "status": "success",
            "data": animal_type.to_dict(),
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


@cached(cache=Cache.REDIS, ttl=86400,
    key_builder=lambda f, session, skip=0, limit=100, category=None, sex=None:
    gen_user_key("system", "animal_types", "list",
                  gen_query_hash({"skip": skip, "limit": limit, "category": category, "sex": sex}))
)
async def get_all_animal_types(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        sex: Optional[str] = None
) -> Dict[str, Any]:
    """Get all animal types with optional filtering"""
    try:
        query = select(AnimalType)

        # Apply filters
        if category:
            try:
                category_enum = AnimalCategory(category)
                query = query.filter(AnimalType.category == category_enum)
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Invalid category: {category}"
                }

        if sex:
            try:
                sex_enum = AnimalSex(sex)
                query = query.filter(AnimalType.sex == sex_enum)
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Invalid sex: {sex}"
                }

        # Add pagination
        query = query.offset(skip).limit(limit)

        result = await session.execute(query)
        animal_types = result.scalars().all()

        animal_type_dicts = [at.to_dict() for at in animal_types]

        return {
            "status": "success",
            "data": animal_type_dicts,
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def update_animal_type(
        session: AsyncSession,
        animal_type_id: str,
        data: Dict[str, Any]
) -> Dict[str, Any]:
    """Update an animal type entry"""
    try:
        query = select(AnimalType).filter(AnimalType.uuid == animal_type_id)
        result = await session.execute(query)
        animal_type = result.scalar_one_or_none()

        if not animal_type:
            return {
                "status": "error",
                "data": None,
                "error": "Animal type not found"
            }

        # Update fields if provided
        if "breed" in data:
            animal_type.breed = data["breed"]

        if "species" in data:
            animal_type.species = data["species"]

        if "category" in data:
            if data["category"] is not None:
                try:
                    animal_type.category = AnimalCategory(data["category"])
                except ValueError:
                    return {
                        "status": "error",
                        "data": None,
                        "error": f"Invalid category: {data['category']}"
                    }
            else:
                return {
                    "status": "error",
                    "data": None,
                    "error": "category is required and cannot be null"
                }

        if "sex" in data:
            if data["sex"] is not None:
                try:
                    animal_type.sex = AnimalSex(data["sex"])
                except ValueError:
                    return {
                        "status": "error",
                        "data": None,
                        "error": f"Invalid sex: {data['sex']}"
                    }
            else:
                animal_type.sex = None

        if "category_type" in data:
            animal_type.category_type = data["category_type"]

        # Update numeric fields
        numeric_fields = [
            "puberty_age", "estrus_cycle_length", "estrus_duration",
            "age_at_first_egg", "days_to_breed", "days_to_market"
        ]

        for field in numeric_fields:
            if field in data:
                setattr(animal_type, field, data[field])

        # Update text fields
        text_fields = [
            "estrus_cycle_type", "best_breeding_time", "heat_signs", "notes"
        ]

        for field in text_fields:
            if field in data:
                setattr(animal_type, field, data[field])

        animal_type.update_timestamp()

        await session.commit()
        await session.refresh(animal_type)

        # Invalidate relevant caches
        await invalidate_patterns("system", [
            "animal_types:*",
            "dashboard",
            "stats:*"
        ])

        return {
            "status": "success",
            "data": animal_type.to_dict(),
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def delete_animal_type(
        session: AsyncSession,
        animal_type_id: str
) -> Dict[str, Any]:
    """Delete an animal type entry"""
    try:
        query = select(AnimalType).filter(AnimalType.uuid == animal_type_id)
        result = await session.execute(query)
        animal_type = result.scalar_one_or_none()

        if not animal_type:
            return {
                "status": "error",
                "data": None,
                "error": "Animal type not found"
            }

        await session.delete(animal_type)
        await session.commit()

        # Invalidate relevant caches
        await invalidate_patterns("system", [
            "animal_types:*",
            "dashboard",
            "stats:*"
        ])

        return {
            "status": "success",
            "data": {"deleted": True, "animal_type_id": animal_type_id},
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


@cached(cache=Cache.REDIS, ttl=3600,
    key_builder=lambda f, session, search_term:
    gen_user_key("system", "animal_types", "search", hashlib.md5(search_term.encode()).hexdigest()[:8])
)
async def search_animal_types(
        session: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 50
) -> Dict[str, Any]:
    """Search animal types by breed or species"""
    try:
        search_pattern = f"%{search_term}%"

        query = select(AnimalType).filter(
            or_(
                AnimalType.breed.ilike(search_pattern),
                AnimalType.species.ilike(search_pattern),
                AnimalType.category_type.ilike(search_pattern)
            )
        ).offset(skip).limit(limit)

        result = await session.execute(query)
        animal_types = result.scalars().all()

        animal_type_dicts = [at.to_dict() for at in animal_types]

        return {
            "status": "success",
            "data": animal_type_dicts,
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def count_animal_types(
        session: AsyncSession,
        category: Optional[str] = None,
        sex: Optional[str] = None
) -> Dict[str, Any]:
    """Count total animal types with optional filtering"""
    try:
        query = select(func.count(AnimalType.id))

        if category:
            try:
                category_enum = AnimalCategory(category)
                query = query.filter(AnimalType.category == category_enum)
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Invalid category: {category}"
                }

        if sex:
            try:
                sex_enum = AnimalSex(sex)
                query = query.filter(AnimalType.sex == sex_enum)
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Invalid sex: {sex}"
                }

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


async def get_animal_type_statistics(session: AsyncSession) -> Dict[str, Any]:
    """Get statistics about animal types in the database"""
    try:
        # Count total animal types
        total_query = select(func.count(AnimalType.id))
        total_result = await session.execute(total_query)
        total_animal_types = total_result.scalar()

        if total_animal_types == 0:
            return {
                "status": "success",
                "data": {
                    "total_animal_types": 0,
                    "by_category": {},
                    "by_sex": {},
                    "avg_days_to_market": 0
                },
                "error": None
            }

        # Count by category
        category_query = select(
            AnimalType.category,
            func.count(AnimalType.id).label('count')
        ).group_by(AnimalType.category)
        category_result = await session.execute(category_query)
        by_category = {
            row.category.value if row.category else "unknown": row.count
            for row in category_result
        }

        # Count by sex
        sex_query = select(
            AnimalType.sex,
            func.count(AnimalType.id).label('count')
        ).group_by(AnimalType.sex)
        sex_result = await session.execute(sex_query)
        by_sex = {
            row.sex.value if row.sex else "unknown": row.count
            for row in sex_result
        }

        # Average days to market
        avg_market_query = select(func.avg(AnimalType.days_to_market)).filter(
            AnimalType.days_to_market.isnot(None)
        )
        avg_market_result = await session.execute(avg_market_query)
        avg_days = avg_market_result.scalar()

        return {
            "status": "success",
            "data": {
                "total_animal_types": total_animal_types,
                "by_category": by_category,
                "by_sex": by_sex,
                "avg_days_to_market": float(avg_days) if avg_days else 0
            },
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }
