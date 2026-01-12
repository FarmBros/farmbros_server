from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum
from datetime import datetime
import uuid
import enum

from models.runner import Base


class AnimalSex(enum.Enum):
    """Biological sex classification"""
    MALE = "male"
    FEMALE = "female"
    MIXED = "mixed"  # For breeding pairs or mixed-sex groups


class AnimalCategory(enum.Enum):
    """Animal category classification"""
    CATTLE = "cattle"
    SHEEP = "sheep"
    GOAT = "goat"
    PIG = "pig"
    CHICKEN = "chicken"
    DUCK = "duck"
    TURKEY = "turkey"
    RABBIT = "rabbit"
    FISH = "fish"
    OTHER = "other"


class AnimalType(Base):
    __tablename__ = 'animal_types'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))

    # Basic identification
    breed = Column(String(255), nullable=False, index=True)
    species = Column(String(255), nullable=True)
    sex = Column(Enum(AnimalSex, name='animalsex', values_callable=lambda x: [e.value for e in x]), nullable=True)

    # Classification
    category = Column(Enum(AnimalCategory, name='animalcategory', values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    category_type = Column(String(100), nullable=True)  # e.g., dairy, beef, layer, broiler

    # Reproductive information
    puberty_age = Column(Integer, nullable=True)  # Age at puberty in days
    estrus_cycle_type = Column(String(100), nullable=True)  # e.g., polyestrous, seasonal, etc.
    estrus_cycle_length = Column(Integer, nullable=True)  # Length of cycle in days
    estrus_duration = Column(Integer, nullable=True)  # Duration of heat in hours
    best_breeding_time = Column(String(255), nullable=True)  # Optimal breeding timing description
    heat_signs = Column(Text, nullable=True)  # Observable signs of heat/estrus
    age_at_first_egg = Column(Integer, nullable=True)  # For poultry, age at first egg in days

    # Production timeline
    days_to_breed = Column(Integer, nullable=True)  # Days from birth to breeding age
    days_to_market = Column(Integer, nullable=True)  # Days to reach market weight/age

    # Additional information
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, breed, category, **kwargs):
        self.breed = breed
        self.category = category
        self.species = kwargs.get('species')
        self.sex = kwargs.get('sex')
        self.category_type = kwargs.get('category_type')
        self.puberty_age = kwargs.get('puberty_age')
        self.estrus_cycle_type = kwargs.get('estrus_cycle_type')
        self.estrus_cycle_length = kwargs.get('estrus_cycle_length')
        self.estrus_duration = kwargs.get('estrus_duration')
        self.best_breeding_time = kwargs.get('best_breeding_time')
        self.heat_signs = kwargs.get('heat_signs')
        self.age_at_first_egg = kwargs.get('age_at_first_egg')
        self.days_to_breed = kwargs.get('days_to_breed')
        self.days_to_market = kwargs.get('days_to_market')
        self.notes = kwargs.get('notes')

    def __repr__(self):
        return f'<AnimalType {self.breed} ({self.category.value if self.category else "Unknown"})>'

    def get_uuid(self):
        return self.uuid

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'breed': self.breed,
            'species': self.species,
            'sex': self.sex.value if self.sex else None,
            'category': self.category.value if self.category else None,
            'category_type': self.category_type,
            'puberty_age': self.puberty_age,
            'estrus_cycle_type': self.estrus_cycle_type,
            'estrus_cycle_length': self.estrus_cycle_length,
            'estrus_duration': self.estrus_duration,
            'best_breeding_time': self.best_breeding_time,
            'heat_signs': self.heat_signs,
            'age_at_first_egg': self.age_at_first_egg,
            'days_to_breed': self.days_to_breed,
            'days_to_market': self.days_to_market,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    def get_breeding_info(self):
        """Returns a summary of breeding information"""
        info = {}
        if self.puberty_age:
            info['puberty_age_days'] = self.puberty_age
        if self.estrus_cycle_length:
            info['cycle_length_days'] = self.estrus_cycle_length
        if self.estrus_duration:
            info['estrus_duration_hours'] = self.estrus_duration
        if self.best_breeding_time:
            info['best_breeding_time'] = self.best_breeding_time
        return info if info else None

    def get_production_timeline(self):
        """Returns production timeline information"""
        timeline = {}
        if self.days_to_breed:
            timeline['days_to_breed'] = self.days_to_breed
        if self.days_to_market:
            timeline['days_to_market'] = self.days_to_market
        if self.age_at_first_egg:
            timeline['age_at_first_egg'] = self.age_at_first_egg
        return timeline if timeline else None