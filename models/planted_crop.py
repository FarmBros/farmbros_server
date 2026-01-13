from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from models.runner import Base


class PlantedCrop(Base):
    __tablename__ = 'planted_crop'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys (using UUIDs)
    crop_id = Column(String(36), ForeignKey('crops.uuid'), nullable=False)
    plot_id = Column(String(36), ForeignKey('plots.uuid'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.uuid'), nullable=False)

    # Planting information
    planting_method = Column(String(100), nullable=True)
    planting_spacing = Column(Float, nullable=True)  # Spacing in meters

    # Timeline dates
    germination_date = Column(DateTime, nullable=True)  # For direct seeded crops
    transplant_date = Column(DateTime, nullable=True)  # For transplanted crops
    seedling_age = Column(Integer, nullable=True)  # Age in days for transplants
    harvest_date = Column(DateTime, nullable=True)  # Expected or actual harvest date

    # Quantity and yield
    number_of_crops = Column(Integer, nullable=True)  # Number of plants
    estimated_yield = Column(Float, nullable=True)  # Expected yield in kg

    # Additional information
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    crop = relationship("Crop", backref="planted_crops")
    plot = relationship("Plot", backref="planted_crops")
    user = relationship("User", backref="planted_crops")

    def __init__(self, crop_id, plot_id, user_id, **kwargs):
        self.crop_id = crop_id
        self.plot_id = plot_id
        self.user_id = user_id
        self.planting_method = kwargs.get('planting_method')
        self.planting_spacing = kwargs.get('planting_spacing')
        self.germination_date = kwargs.get('germination_date')
        self.transplant_date = kwargs.get('transplant_date')
        self.seedling_age = kwargs.get('seedling_age')
        self.harvest_date = kwargs.get('harvest_date')
        self.number_of_crops = kwargs.get('number_of_crops')
        self.estimated_yield = kwargs.get('estimated_yield')
        self.notes = kwargs.get('notes')

    def __repr__(self):
        return f'<PlantedCrop {self.uuid} - Crop:{self.crop_id} Plot:{self.plot_id}>'

    def get_uuid(self):
        return self.uuid

    def to_dict(self):
        # Foreign keys are now UUIDs in the database, return them directly
        return {
            'id': self.id,
            'uuid': self.uuid,
            'crop_id': self.crop_id,
            'plot_id': self.plot_id,
            'user_id': self.user_id,
            'planting_method': self.planting_method,
            'planting_spacing': self.planting_spacing,
            'germination_date': self.germination_date.isoformat() if self.germination_date else None,
            'transplant_date': self.transplant_date.isoformat() if self.transplant_date else None,
            'seedling_age': self.seedling_age,
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else None,
            'number_of_crops': self.number_of_crops,
            'estimated_yield': self.estimated_yield,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

    def get_planting_date(self):
        """Returns the earliest planting date (germination or transplant)"""
        if self.germination_date and self.transplant_date:
            return min(self.germination_date, self.transplant_date)
        return self.germination_date or self.transplant_date

    def calculate_days_to_harvest(self):
        """Calculate days from planting to harvest"""
        planting_date = self.get_planting_date()
        if planting_date and self.harvest_date:
            return (self.harvest_date - planting_date).days
        return None
