from typing import Optional, Dict, Any, List
import hashlib
import json
import os
from pathlib import Path

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from aiocache import Cache, cached

from models.crop import Crop, CropGroup, Lifecycle, SeedlingType
from services.caching import *


async def create_crop(
        session: AsyncSession,
        data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a new crop entry"""
    try:
        common_name = data.get("common_name")
        if not common_name:
            return {
                "status": "error",
                "data": None,
                "error": "common_name is required"
            }

        # Parse enums if provided
        crop_group = None
        if data.get("crop_group"):
            try:
                crop_group = CropGroup(data["crop_group"])
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Invalid crop_group: {data['crop_group']}"
                }

        lifecycle = None
        if data.get("lifecycle"):
            try:
                lifecycle = Lifecycle(data["lifecycle"])
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Invalid lifecycle: {data['lifecycle']}"
                }

        seedling_type = None
        if data.get("seedling_type"):
            try:
                seedling_type = SeedlingType(data["seedling_type"])
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Invalid seedling_type: {data['seedling_type']}"
                }

        crop = Crop(
            common_name=common_name,
            genus=data.get("genus"),
            species=data.get("species"),
            crop_group=crop_group,
            lifecycle=lifecycle,
            germination_days=data.get("germination_days"),
            days_to_transplant=data.get("days_to_transplant"),
            days_to_maturity=data.get("days_to_maturity"),
            nitrogen_needs=data.get("nitrogen_needs"),
            phosphorus_needs=data.get("phosphorus_needs"),
            potassium_needs=data.get("potassium_needs"),
            water_coefficient=data.get("water_coefficient"),
            planting_methods=data.get("planting_methods"),
            planting_spacing_m=data.get("planting_spacing_m"),
            row_spacing_m=data.get("row_spacing_m"),
            seedling_type=seedling_type,
            notes=data.get("notes")
        )

        session.add(crop)
        await session.commit()
        await session.refresh(crop)

        # Invalidate relevant caches
        await invalidate_patterns("system", [
            "crops:*",
            "dashboard",
            "stats:*"
        ])

        return {
            "status": "success",
            "data": crop.to_dict(),
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def get_crop(
        session: AsyncSession,
        crop_id: str
) -> Dict[str, Any]:
    """Get a single crop by UUID"""
    try:
        query = select(Crop).filter(Crop.uuid == crop_id)
        result = await session.execute(query)
        crop = result.scalar_one_or_none()

        if not crop:
            return {
                "status": "error",
                "data": None,
                "error": "Crop not found"
            }

        return {
            "status": "success",
            "data": crop.to_dict(),
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


@cached(cache=Cache.REDIS, ttl=86400,
    key_builder=lambda f, session, skip=0, limit=100, crop_group=None, lifecycle=None:
    gen_user_key("system", "crops", "list",
                  gen_query_hash({"skip": skip, "limit": limit, "crop_group": crop_group, "lifecycle": lifecycle}))
)
async def get_all_crops(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        crop_group: Optional[str] = None,
        lifecycle: Optional[str] = None
) -> Dict[str, Any]:
    """Get all crops with optional filtering"""
    try:
        query = select(Crop)

        # Apply filters
        if crop_group:
            try:
                crop_group_enum = CropGroup(crop_group)
                query = query.filter(Crop.crop_group == crop_group_enum)
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Invalid crop_group: {crop_group}"
                }

        if lifecycle:
            try:
                lifecycle_enum = Lifecycle(lifecycle)
                query = query.filter(Crop.lifecycle == lifecycle_enum)
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Invalid lifecycle: {lifecycle}"
                }

        # Add pagination
        query = query.offset(skip).limit(limit)

        result = await session.execute(query)
        crops = result.scalars().all()

        crop_dicts = [crop.to_dict() for crop in crops]

        return {
            "status": "success",
            "data": crop_dicts,
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def update_crop(
        session: AsyncSession,
        crop_id: str,
        data: Dict[str, Any]
) -> Dict[str, Any]:
    """Update a crop entry"""
    try:
        query = select(Crop).filter(Crop.uuid == crop_id)
        result = await session.execute(query)
        crop = result.scalar_one_or_none()

        if not crop:
            return {
                "status": "error",
                "data": None,
                "error": "Crop not found"
            }

        # Update fields if provided
        if "common_name" in data:
            crop.common_name = data["common_name"]

        if "genus" in data:
            crop.genus = data["genus"]

        if "species" in data:
            crop.species = data["species"]

        if "crop_group" in data:
            if data["crop_group"] is not None:
                try:
                    crop.crop_group = CropGroup(data["crop_group"])
                except ValueError:
                    return {
                        "status": "error",
                        "data": None,
                        "error": f"Invalid crop_group: {data['crop_group']}"
                    }
            else:
                crop.crop_group = None

        if "lifecycle" in data:
            if data["lifecycle"] is not None:
                try:
                    crop.lifecycle = Lifecycle(data["lifecycle"])
                except ValueError:
                    return {
                        "status": "error",
                        "data": None,
                        "error": f"Invalid lifecycle: {data['lifecycle']}"
                    }
            else:
                crop.lifecycle = None

        if "seedling_type" in data:
            if data["seedling_type"] is not None:
                try:
                    crop.seedling_type = SeedlingType(data["seedling_type"])
                except ValueError:
                    return {
                        "status": "error",
                        "data": None,
                        "error": f"Invalid seedling_type: {data['seedling_type']}"
                    }
            else:
                crop.seedling_type = None

        # Update numeric fields
        numeric_fields = [
            "germination_days", "days_to_transplant", "days_to_maturity",
            "nitrogen_needs", "phosphorus_needs", "potassium_needs",
            "water_coefficient", "planting_spacing_m", "row_spacing_m"
        ]

        for field in numeric_fields:
            if field in data:
                setattr(crop, field, data[field])

        # Update text fields
        if "planting_methods" in data:
            crop.planting_methods = data["planting_methods"]

        if "notes" in data:
            crop.notes = data["notes"]

        crop.update_timestamp()

        await session.commit()
        await session.refresh(crop)

        # Invalidate relevant caches
        await invalidate_patterns("system", [
            "crops:*",
            "dashboard",
            "stats:*"
        ])

        return {
            "status": "success",
            "data": crop.to_dict(),
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def delete_crop(
        session: AsyncSession,
        crop_id: str
) -> Dict[str, Any]:
    """Delete a crop entry"""
    try:
        query = select(Crop).filter(Crop.uuid == crop_id)
        result = await session.execute(query)
        crop = result.scalar_one_or_none()

        if not crop:
            return {
                "status": "error",
                "data": None,
                "error": "Crop not found"
            }

        await session.delete(crop)
        await session.commit()

        # Invalidate relevant caches
        await invalidate_patterns("system", [
            "crops:*",
            "dashboard",
            "stats:*"
        ])

        return {
            "status": "success",
            "data": {"deleted": True, "crop_id": crop_id},
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
    gen_user_key("system", "crops", "search", hashlib.md5(search_term.encode()).hexdigest()[:8])
)
async def search_crops(
        session: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 50
) -> Dict[str, Any]:
    """Search crops by common name, genus, or species"""
    try:
        search_pattern = f"%{search_term}%"

        query = select(Crop).filter(
            or_(
                Crop.common_name.ilike(search_pattern),
                Crop.genus.ilike(search_pattern),
                Crop.species.ilike(search_pattern)
            )
        ).offset(skip).limit(limit)

        result = await session.execute(query)
        crops = result.scalars().all()

        crop_dicts = [crop.to_dict() for crop in crops]

        return {
            "status": "success",
            "data": crop_dicts,
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


async def count_crops(
        session: AsyncSession,
        crop_group: Optional[str] = None,
        lifecycle: Optional[str] = None
) -> Dict[str, Any]:
    """Count total crops with optional filtering"""
    try:
        query = select(func.count(Crop.id))

        if crop_group:
            try:
                crop_group_enum = CropGroup(crop_group)
                query = query.filter(Crop.crop_group == crop_group_enum)
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Invalid crop_group: {crop_group}"
                }

        if lifecycle:
            try:
                lifecycle_enum = Lifecycle(lifecycle)
                query = query.filter(Crop.lifecycle == lifecycle_enum)
            except ValueError:
                return {
                    "status": "error",
                    "data": None,
                    "error": f"Invalid lifecycle: {lifecycle}"
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


async def get_crop_statistics(session: AsyncSession) -> Dict[str, Any]:
    """Get statistics about crops in the database"""
    try:
        # Count total crops
        total_query = select(func.count(Crop.id))
        total_result = await session.execute(total_query)
        total_crops = total_result.scalar()

        if total_crops == 0:
            return {
                "status": "success",
                "data": {
                    "total_crops": 0,
                    "by_crop_group": {},
                    "by_lifecycle": {},
                    "avg_days_to_maturity": 0
                },
                "error": None
            }

        # Count by crop group
        crop_group_query = select(
            Crop.crop_group,
            func.count(Crop.id).label('count')
        ).group_by(Crop.crop_group)
        crop_group_result = await session.execute(crop_group_query)
        by_crop_group = {
            row.crop_group.value if row.crop_group else "unknown": row.count
            for row in crop_group_result
        }

        # Count by lifecycle
        lifecycle_query = select(
            Crop.lifecycle,
            func.count(Crop.id).label('count')
        ).group_by(Crop.lifecycle)
        lifecycle_result = await session.execute(lifecycle_query)
        by_lifecycle = {
            row.lifecycle.value if row.lifecycle else "unknown": row.count
            for row in lifecycle_result
        }

        # Average days to maturity
        avg_maturity_query = select(func.avg(Crop.days_to_maturity)).filter(
            Crop.days_to_maturity.isnot(None)
        )
        avg_maturity_result = await session.execute(avg_maturity_query)
        avg_days = avg_maturity_result.scalar()

        return {
            "status": "success",
            "data": {
                "total_crops": total_crops,
                "by_crop_group": by_crop_group,
                "by_lifecycle": by_lifecycle,
                "avg_days_to_maturity": float(avg_days) if avg_days else 0
            },
            "error": None
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }


def map_crop_group(crop_group_str: str) -> Optional[CropGroup]:
    """Map crop group string from dataset to CropGroup enum"""
    mapping = {
        "Fruit and nuts": CropGroup.FRUIT,
        "Vegetables and melons": CropGroup.VEGETABLE,
        "Cereals": CropGroup.CEREAL,
        "Leguminous crops": CropGroup.LEGUME,
        "High starch root/tuber crops": CropGroup.ROOT,
        "Potatoes and yams": CropGroup.TUBER,
        "Root, bulb or tuberous vegetables": CropGroup.ROOT,
        "Leafy or stem vegetables": CropGroup.LEAFY_GREEN,
        "Stimulant, spice and aromatic crops": CropGroup.HERB,
        "Spice and aromatic crops": CropGroup.HERB,
        "Medicinal, pesticidal or similar crops": CropGroup.HERB,
        "Other crops": CropGroup.OTHER,
        "Sugar crops": CropGroup.OTHER,
        "Oilseed crops and oleaginous fruits": CropGroup.OTHER,
        "Fibre crops": CropGroup.OTHER,
        "Grasses and other fodder crops": CropGroup.OTHER,
        "Flower crops": CropGroup.FLOWER,
    }
    return mapping.get(crop_group_str)


def map_seedling_type(seeding_type_str: str, needs_transplant: bool) -> Optional[SeedlingType]:
    """Map seeding type from dataset to SeedlingType enum"""
    if seeding_type_str == "SEED":
        if needs_transplant:
            return SeedlingType.TRANSPLANT
        else:
            return SeedlingType.DIRECT_SEED
    elif seeding_type_str == "SEEDLING_OR_PLANTING_STOCK":
        return SeedlingType.TRANSPLANT
    return None


def load_crops_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Load crop data from JSON file"""
    try:
        # Get the project root directory (parent of controllers directory)
        project_root = Path(__file__).parent.parent

        # If file_path is relative, resolve it relative to project root
        if not os.path.isabs(file_path):
            full_path = project_root / file_path
        else:
            full_path = Path(file_path)

        print(f"Loading crops from: {full_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            crops_data = json.load(f)

        print(f"Successfully loaded {len(crops_data)} crops")
        return crops_data

    except FileNotFoundError:
        print(f"Error: File not found: {full_path if 'full_path' in locals() else file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return []
    except Exception as e:
        print(f"Error loading crops file: {e}")
        return []


async def import_crops_from_dataset(
        session: AsyncSession,
        file_path: str = "assets/cropV2.json",
        skip_existing: bool = True
) -> Dict[str, Any]:
    """
    Import crops from the dataset file into the database

    Args:
        session: Database session
        file_path: Path to the cropV2.json file
        skip_existing: If True, skip crops that already exist by common_name
    """
    try:
        # Load the crops data
        crops_data = load_crops_from_json(file_path)

        if not crops_data:
            return {
                "status": "error",
                "data": None,
                "error": "Failed to parse crops data from file"
            }

        created_count = 0
        skipped_count = 0
        error_count = 0
        errors = []

        for crop_data in crops_data:
            try:
                common_name = crop_data.get("crop_common_name")
                if not common_name:
                    error_count += 1
                    errors.append(f"Crop missing common_name: {crop_data}")
                    continue

                # Check if crop already exists
                if skip_existing:
                    existing_query = select(Crop).filter(Crop.common_name == common_name)
                    existing_result = await session.execute(existing_query)
                    if existing_result.scalar_one_or_none():
                        skipped_count += 1
                        continue

                # Map crop group
                crop_group = None
                if crop_data.get("crop_group"):
                    crop_group = map_crop_group(crop_data["crop_group"])

                # Map lifecycle
                lifecycle = None
                if crop_data.get("lifecycle"):
                    try:
                        lifecycle = Lifecycle(crop_data["lifecycle"].lower())
                    except ValueError:
                        pass

                # Map seedling type
                seedling_type = None
                if crop_data.get("seeding_type"):
                    seedling_type = map_seedling_type(
                        crop_data["seeding_type"],
                        crop_data.get("needs_transplant", False)
                    )

                # Create crop
                crop = Crop(
                    common_name=common_name,
                    genus=crop_data.get("crop_genus"),
                    species=crop_data.get("crop_specie"),
                    crop_group=crop_group,
                    lifecycle=lifecycle,
                    germination_days=crop_data.get("germination_days"),
                    days_to_transplant=crop_data.get("transplant_days"),
                    days_to_maturity=crop_data.get("harvest_days"),
                    planting_spacing_m=crop_data.get("plant_spacing"),
                    row_spacing_m=None,  # Not in dataset
                    seedling_type=seedling_type,
                    planting_methods=crop_data.get("planting_method"),
                    yield_per_plant=crop_data.get("yield_per_plant"),
                    yield_per_area=crop_data.get("yield_per_area"),
                    notes=f"Subgroup: {crop_data.get('crop_subgroup', 'N/A')}"
                )

                session.add(crop)
                created_count += 1

                # Commit in batches of 50
                if created_count % 50 == 0:
                    await session.flush()

            except Exception as e:
                error_count += 1
                errors.append(f"Error importing {crop_data.get('crop_common_name', 'unknown')}: {str(e)}")
                continue

        # Final commit
        await session.commit()

        # Invalidate caches
        await invalidate_patterns("system", [
            "crops:*",
            "dashboard",
            "stats:*"
        ])

        return {
            "status": "success",
            "data": {
                "created": created_count,
                "skipped": skipped_count,
                "errors": error_count,
                "error_details": errors[:10] if errors else []  # Return first 10 errors
            },
            "error": None
        }

    except Exception as e:
        await session.rollback()
        return {
            "status": "error",
            "data": None,
            "error": str(e)
        }
