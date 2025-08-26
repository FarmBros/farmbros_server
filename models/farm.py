from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import uuid
from datetime import datetime

from models.runner import Base


class Farm(Base):
    __tablename__ = 'farms'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    owner_id = Column(String(36), ForeignKey('users.uuid'), nullable=False)

    boundary = Column(Geography('POLYGON', srid=4326), nullable=False)

    # Optional: Store centroid for quick location queries
    centroid = Column(Geography('POINT', srid=4326))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    description = Column(Text)

    # Area in square meters (calculated from geometry)
    area_sqm = Column(Float)

    # Relationships
    # plots = relationship("Plot", backref="farm", cascade="all, delete-orphan")
    owner = relationship("User", back_populates="farms")

    def __init__(self, name, owner_id, **kwargs):
        self.name = name
        self.owner_id = owner_id
        self.description = kwargs.get('description')
        # Boundary and centroid will be set via CRUD operations

    def __repr__(self):
        return f'<Farm {self.name}>'

    def get_uuid(self):
        """Get the UUID of the farm."""
        return self.uuid

    def to_dict(self, include_geometry=False):
        """Convert farm object to dictionary."""
        farm_dict = {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'owner_id': self.owner_id,
            'description': self.description,
            'area_sqm': self.area_sqm,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_geometry and hasattr(self, 'boundary_geojson'):
            farm_dict['boundary'] = self.boundary_geojson

        if include_geometry and hasattr(self, 'centroid_geojson'):
            farm_dict['centroid'] = self.centroid_geojson

        return farm_dict

    def is_owner(self, user_id):
        """Check if a user is the owner of this farm."""
        return self.owner_id == user_id

    def get_area_in_hectares(self):
        """Convert area from square meters to hectares."""
        if self.area_sqm:
            return self.area_sqm / 10000
        return None

    def get_area_in_acres(self):
        """Convert area from square meters to acres."""
        if self.area_sqm:
            return self.area_sqm / 4047
        return None

    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()