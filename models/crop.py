from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum
from datetime import datetime
import uuid
import enum

from models.runner import Base


class CropGroup(enum.Enum):
    """Crop classification groups"""
    FRUIT = "fruit"
    VEGETABLE = "vegetable"
    CEREAL = "cereal"
    LEGUME = "legume"
    ROOT = "root"
    TUBER = "tuber"
    LEAFY_GREEN = "leafy_green"
    HERB = "herb"
    FLOWER = "flower"
    OTHER = "other"


class Lifecycle(enum.Enum):
    """Plant lifecycle types"""
    ANNUAL = "annual"
    PERENNIAL = "perennial"
    BIENNIAL = "biennial"


class SeedlingType(enum.Enum):
    """Methods of starting crops"""
    DIRECT_SEED = "direct_seed"
    TRANSPLANT = "transplant"
    BOTH = "both"


class Crop(Base):
    __tablename__ = 'crops'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))

    # Basic identification
    common_name = Column(String(255), nullable=False, index=True)
    genus = Column(String(100), nullable=True)
    species = Column(String(100), nullable=True)

    # Classification
    crop_group = Column(Enum(CropGroup, name='cropgroup', values_callable=lambda x: [e.value for e in x]), nullable=True)
    lifecycle = Column(Enum(Lifecycle, name='lifecycle', values_callable=lambda x: [e.value for e in x]), nullable=True)

    # Maturity timeline (in days)
    germination_days = Column(Integer, nullable=True)
    days_to_transplant = Column(Integer, nullable=True)
    days_to_maturity = Column(Integer, nullable=True)

    # Nutrients needed (mg per plant or per square meter)
    nitrogen_needs = Column(Float, nullable=True)
    phosphorus_needs = Column(Float, nullable=True)
    potassium_needs = Column(Float, nullable=True)

    # Water requirements
    water_coefficient = Column(Float, nullable=True)  # Relative water needs (0-1 scale)

    # Yield information
    yield_per_plant = Column(Float, nullable=True)  # Expected yield per plant in kg
    yield_per_area = Column(Float, nullable=True)  # Expected yield per square meter in kg

    # Planting information
    planting_methods = Column(Text, nullable=True)  # JSON or comma-separated list
    planting_spacing_m = Column(Float, nullable=True)  # Spacing between plants in meters
    row_spacing_m = Column(Float, nullable=True)  # Spacing between rows in meters
    seedling_type = Column(Enum(SeedlingType, name='seedlingtype', values_callable=lambda x: [e.value for e in x]), nullable=True)

    # Additional information
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, common_name, **kwargs):
        self.common_name = common_name
        self.genus = kwargs.get('genus')
        self.species = kwargs.get('species')
        self.crop_group = kwargs.get('crop_group')
        self.lifecycle = kwargs.get('lifecycle')
        self.germination_days = kwargs.get('germination_days')
        self.days_to_transplant = kwargs.get('days_to_transplant')
        self.days_to_maturity = kwargs.get('days_to_maturity')
        self.nitrogen_needs = kwargs.get('nitrogen_needs')
        self.phosphorus_needs = kwargs.get('phosphorus_needs')
        self.potassium_needs = kwargs.get('potassium_needs')
        self.water_coefficient = kwargs.get('water_coefficient')
        self.yield_per_plant = kwargs.get('yield_per_plant')
        self.yield_per_area = kwargs.get('yield_per_area')
        self.planting_methods = kwargs.get('planting_methods')
        self.planting_spacing_m = kwargs.get('planting_spacing_m')
        self.row_spacing_m = kwargs.get('row_spacing_m')
        self.seedling_type = kwargs.get('seedling_type')
        self.notes = kwargs.get('notes')

    def __repr__(self):
        scientific_name = f'{self.genus} {self.species}' if self.genus and self.species else 'Unknown'
        return f'<Crop {self.common_name} ({scientific_name})>'

    def get_uuid(self):
        return self.uuid

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'common_name': self.common_name,
            'genus': self.genus,
            'species': self.species,
            'scientific_name': f'{self.genus} {self.species}' if self.genus and self.species else None,
            'crop_group': self.crop_group.value if self.crop_group else None,
            'lifecycle': self.lifecycle.value if self.lifecycle else None,
            'germination_days': self.germination_days,
            'days_to_transplant': self.days_to_transplant,
            'days_to_maturity': self.days_to_maturity,
            'nitrogen_needs': self.nitrogen_needs,
            'phosphorus_needs': self.phosphorus_needs,
            'potassium_needs': self.potassium_needs,
            'water_coefficient': self.water_coefficient,
            'yield_per_plant': self.yield_per_plant,
            'yield_per_area': self.yield_per_area,
            'planting_methods': self.planting_methods,
            'planting_spacing_m': self.planting_spacing_m,
            'row_spacing_m': self.row_spacing_m,
            'seedling_type': self.seedling_type.value if self.seedling_type else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    def get_scientific_name(self):
        """Returns the full scientific name (Genus species)"""
        if self.genus and self.species:
            return f'{self.genus} {self.species}'
        return None

    def get_total_days_from_seed(self):
        """Calculate total days from seeding to maturity"""
        if self.days_to_maturity:
            return self.days_to_maturity
        return None

    def get_npk_ratio(self):
        """Get NPK ratio as a formatted string"""
        if all([self.nitrogen_needs, self.phosphorus_needs, self.potassium_needs]):
            # Normalize to smallest value
            min_val = min(self.nitrogen_needs, self.phosphorus_needs, self.potassium_needs)
            if min_val > 0:
                n = round(self.nitrogen_needs / min_val, 1)
                p = round(self.phosphorus_needs / min_val, 1)
                k = round(self.potassium_needs / min_val, 1)
                return f'{n}-{p}-{k}'
        return None
