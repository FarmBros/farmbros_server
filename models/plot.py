from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from datetime import datetime
import uuid
import enum

from models.runner import Base



plot_types = [
    "field",
    "barn",
    "pasture",
    "green-house",
    "chicken-pen",
    "cow-shed",
    "fish-pond",
    "residence",
    "natural-area",
    "water-source"
]

class PlotType(enum.Enum):
    FIELD = "field"
    BARN = "barn"
    PASTURE = "pasture"
    GREEN_HOUSE = "green-house"
    CHICKEN_PEN = "chicken-pen"
    COW_SHED = "cow-shed"
    FISH_POND = "fish-pond"
    RESIDENCE = "residence"
    NATURAL_AREA = "natural-area"
    WATER_SOURCE = "water-source"

class Plot(Base):
    __tablename__ = 'plots'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    farm_id = Column(Integer, ForeignKey('farms.id'), nullable=False)

    # Plot characteristics
    plot_number = Column(String(50))  # e.g., "A1", "B2", etc.
    plot_type = Column(Enum(PlotType), default=PlotType.FIELD, nullable=False)

    # Geometry - polygon for plot boundary
    boundary = Column(Geography('POLYGON', srid=4326), nullable=False)
    centroid = Column(Geography('POINT', srid=4326))

    # Area and measurements
    area_sqm = Column(Float)

    # Notes and metadata
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    farm = relationship("Farm", back_populates="plots")
    plot_type_data = relationship("PlotTypeBase", back_populates="plot", cascade="all, delete-orphan", uselist=False)

    def __init__(self, name, farm_id, plot_type=PlotType.FIELD, **kwargs):
        self.name = name
        self.farm_id = farm_id
        self.plot_type = plot_type
        self.plot_number = kwargs.get('plot_number')
        self.elevation = kwargs.get('elevation')
        self.slope = kwargs.get('slope')

    def __repr__(self):
        return f'<Plot {self.name} - {self.plot_number}>'

    def get_uuid(self):
        return self.uuid

    def to_dict(self, include_geometry=False, include_type_data=False):
        plot_dict = {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'farm_id': self.farm_id,
            'plot_number': self.plot_number,
            'plot_type': self.plot_type.value if self.plot_type else None,

            'area_sqm': self.area_sqm,

            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_geometry and hasattr(self, 'boundary_geojson'):
            plot_dict['boundary'] = self.boundary_geojson

        if include_geometry and hasattr(self, 'centroid_geojson'):
            plot_dict['centroid'] = self.centroid_geojson

        if include_type_data and self.plot_type_data:
            plot_dict['plot_type_data'] = self.plot_type_data.to_dict()

        return plot_dict

    def get_area_in_hectares(self):
        if self.area_sqm:
            return self.area_sqm / 10000
        return None

    def get_area_in_acres(self):
        if self.area_sqm:
            return self.area_sqm / 4047
        return None

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
