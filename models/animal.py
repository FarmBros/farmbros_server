from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from models.runner import Base


class Animal(Base):
    __tablename__ = 'animals'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys - relationships to other tables
    farm_id = Column(Integer, ForeignKey('farms.id'), nullable=False)
    plot_id = Column(Integer, ForeignKey('plots.id'), nullable=True)
    animal_type_id = Column(Integer, ForeignKey('animal_types.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Basic identification
    name = Column(String(255), nullable=False)  # Individual name or batch name
    identifier = Column(String(100), nullable=True, index=True)  # Tag ID or other identifier
    color = Column(String(100), nullable=True)
    use = Column(String(255), nullable=True)  # Purpose: milk, eggs, meat, breeding, etc.

    # Batch information
    is_batch = Column(Boolean, default=False, nullable=False)
    batch_count = Column(Integer, nullable=True)  # Number of animals in batch

    # Important dates
    birth_date = Column(Date, nullable=True)
    brought_in_date = Column(Date, nullable=True)  # Date animal was acquired/brought to farm
    weaning_date = Column(Date, nullable=True)
    removal_date = Column(Date, nullable=True)  # Date animal was sold/died/removed

    # Optional parent tracking (JSON format)
    parents_id = Column(JSON, nullable=True)  # e.g., {"mother_id": "uuid", "father_id": "uuid"}

    # Additional information
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    farm = relationship("Farm", backref="animals")
    plot = relationship("Plot", backref="animals")
    animal_type = relationship("AnimalType", backref="animals")
    user = relationship("User", backref="animals")

    def __init__(self, farm_id, animal_type_id, user_id, name, **kwargs):
        self.farm_id = farm_id
        self.animal_type_id = animal_type_id
        self.user_id = user_id
        self.name = name
        self.plot_id = kwargs.get('plot_id')
        self.identifier = kwargs.get('identifier')
        self.color = kwargs.get('color')
        self.use = kwargs.get('use')
        self.is_batch = kwargs.get('is_batch', False)
        self.batch_count = kwargs.get('batch_count')
        self.birth_date = kwargs.get('birth_date')
        self.brought_in_date = kwargs.get('brought_in_date')
        self.weaning_date = kwargs.get('weaning_date')
        self.removal_date = kwargs.get('removal_date')
        self.parents_id = kwargs.get('parents_id')
        self.notes = kwargs.get('notes')

    def __repr__(self):
        batch_info = f'Batch({self.batch_count})' if self.is_batch else 'Individual'
        return f'<Animal {self.name} - {batch_info} Type:{self.animal_type_id}>'

    def get_uuid(self):
        return self.uuid

    def to_dict(self):
        # Return UUIDs for foreign key fields (per API convention)
        # Check if relationships are loaded to avoid triggering lazy loads
        farm_uuid = self.farm.uuid if hasattr(self, 'farm') and self.farm else None
        plot_uuid = self.plot.uuid if hasattr(self, 'plot') and self.plot else None
        animal_type_uuid = self.animal_type.uuid if hasattr(self, 'animal_type') and self.animal_type else None
        user_uuid = self.user.uuid if hasattr(self, 'user') and self.user else None

        return {
            'id': self.id,
            'uuid': self.uuid,
            'farm_id': farm_uuid,
            'plot_id': plot_uuid,
            'animal_type_id': animal_type_uuid,
            'user_id': user_uuid,
            'name': self.name,
            'identifier': self.identifier,
            'color': self.color,
            'use': self.use,
            'is_batch': self.is_batch,
            'batch_count': self.batch_count,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'brought_in_date': self.brought_in_date.isoformat() if self.brought_in_date else None,
            'weaning_date': self.weaning_date.isoformat() if self.weaning_date else None,
            'removal_date': self.removal_date.isoformat() if self.removal_date else None,
            'parents_id': self.parents_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    def get_age_in_days(self):
        """Calculate age in days from birth date or brought in date"""
        if self.birth_date:
            reference_date = self.removal_date if self.removal_date else datetime.now().date()
            return (reference_date - self.birth_date).days
        return None

    def get_time_on_farm_days(self):
        """Calculate how long the animal has been on the farm"""
        if self.brought_in_date:
            reference_date = self.removal_date if self.removal_date else datetime.now().date()
            return (reference_date - self.brought_in_date).days
        return None

    def is_active(self):
        """Check if animal is currently active (not removed)"""
        return self.removal_date is None

    def get_weaning_age_days(self):
        """Calculate age at weaning"""
        if self.birth_date and self.weaning_date:
            return (self.weaning_date - self.birth_date).days
        return None
