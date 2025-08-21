from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from datetime import datetime
import uuid
import enum

from models.runner import Base


class PlotStatus(enum.Enum):
    ACTIVE = "active"
    FALLOW = "fallow"
    PREPARING = "preparing"
    HARVESTED = "harvested"
    MAINTENANCE = "maintenance"


class PlotType(enum.Enum):
    CROP = "crop"
    LIVESTOCK = "livestock"
    MIXED = "mixed"
    FORESTRY = "forestry"
    AQUACULTURE = "aquaculture"
    GREENHOUSE = "greenhouse"
    ORCHARD = "orchard"
    PASTURE = "pasture"


class Plot(Base):
    __tablename__ = 'plots'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    farm_id = Column(Integer, ForeignKey('farms.id'), nullable=False)

    # Plot characteristics
    plot_number = Column(String(50))  # e.g., "A1", "B2", etc.
    plot_type = Column(Enum(PlotType), default=PlotType.CROP, nullable=False)
    status = Column(Enum(PlotStatus), default=PlotStatus.PREPARING, nullable=False)

    # Geometry - polygon for plot boundary
    boundary = Column(Geometry('POLYGON'), nullable=False)
    centroid = Column(Geometry('POINT'))

    # Area and measurements
    area_sqm = Column(Float)
    elevation = Column(Float)  # Average elevation in meters
    slope = Column(Float)  # Average slope in degrees

    # Agricultural data
    soil_type = Column(String(100))
    ph_level = Column(Float)
    nitrogen_level = Column(Float)
    phosphorus_level = Column(Float)
    potassium_level = Column(Float)
    organic_matter = Column(Float)  # Percentage

    # Current crop/livestock information
    current_crop = Column(String(100))
    crop_variety = Column(String(100))
    planting_date = Column(DateTime)
    expected_harvest_date = Column(DateTime)
    last_harvest_date = Column(DateTime)

    # Livestock specific (if applicable)
    livestock_type = Column(String(100))
    livestock_count = Column(Integer)
    grazing_capacity = Column(Integer)

    # Water and irrigation
    irrigation_type = Column(String(50))  # drip, sprinkler, flood, none
    water_source = Column(String(100))

    # Notes and metadata
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    farm = relationship("Farm", back_populates="plots")

    def __init__(self, name, farm_id, plot_type=PlotType.CROP, **kwargs):
        self.name = name
        self.farm_id = farm_id
        self.plot_type = plot_type
        self.status = kwargs.get('status', PlotStatus.PREPARING)
        self.plot_number = kwargs.get('plot_number')
        self.soil_type = kwargs.get('soil_type')
        self.current_crop = kwargs.get('current_crop')
        self.crop_variety = kwargs.get('crop_variety')
        self.livestock_type = kwargs.get('livestock_type')
        self.livestock_count = kwargs.get('livestock_count')
        self.irrigation_type = kwargs.get('irrigation_type')
        self.water_source = kwargs.get('water_source')
        self.notes = kwargs.get('notes')
        self.ph_level = kwargs.get('ph_level')
        self.nitrogen_level = kwargs.get('nitrogen_level')
        self.phosphorus_level = kwargs.get('phosphorus_level')
        self.potassium_level = kwargs.get('potassium_level')
        self.organic_matter = kwargs.get('organic_matter')
        self.elevation = kwargs.get('elevation')
        self.slope = kwargs.get('slope')
        self.grazing_capacity = kwargs.get('grazing_capacity')

    def __repr__(self):
        return f'<Plot {self.name} - {self.plot_number}>'

    def get_uuid(self):
        return self.uuid

    def to_dict(self, include_geometry=False):
        plot_dict = {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'farm_id': self.farm_id,
            'plot_number': self.plot_number,
            'plot_type': self.plot_type.value if self.plot_type else None,
            'status': self.status.value if self.status else None,
            'area_sqm': self.area_sqm,
            'elevation': self.elevation,
            'slope': self.slope,
            'soil_type': self.soil_type,
            'ph_level': self.ph_level,
            'nitrogen_level': self.nitrogen_level,
            'phosphorus_level': self.phosphorus_level,
            'potassium_level': self.potassium_level,
            'organic_matter': self.organic_matter,
            'current_crop': self.current_crop,
            'crop_variety': self.crop_variety,
            'planting_date': self.planting_date.isoformat() if self.planting_date else None,
            'expected_harvest_date': self.expected_harvest_date.isoformat() if self.expected_harvest_date else None,
            'last_harvest_date': self.last_harvest_date.isoformat() if self.last_harvest_date else None,
            'livestock_type': self.livestock_type,
            'livestock_count': self.livestock_count,
            'grazing_capacity': self.grazing_capacity,
            'irrigation_type': self.irrigation_type,
            'water_source': self.water_source,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_geometry and hasattr(self, 'boundary_geojson'):
            plot_dict['boundary'] = self.boundary_geojson

        if include_geometry and hasattr(self, 'centroid_geojson'):
            plot_dict['centroid'] = self.centroid_geojson

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

    def is_active(self):
        return self.status == PlotStatus.ACTIVE

    def is_ready_for_planting(self):
        return self.status in [PlotStatus.PREPARING, PlotStatus.FALLOW, PlotStatus.HARVESTED]

    def set_crop(self, crop_name, variety=None, planting_date=None):
        self.current_crop = crop_name
        self.crop_variety = variety
        self.planting_date = planting_date or datetime.utcnow()
        self.status = PlotStatus.ACTIVE

    def set_harvest_date(self, harvest_date):
        self.expected_harvest_date = harvest_date

    def mark_as_harvested(self):
        self.status = PlotStatus.HARVESTED
        self.last_harvest_date = datetime.utcnow()
        self.current_crop = None
        self.crop_variety = None
        self.planting_date = None
        self.expected_harvest_date = None

    def mark_as_fallow(self):
        self.status = PlotStatus.FALLOW
        self.current_crop = None
        self.crop_variety = None

    def update_soil_data(self, ph=None, nitrogen=None, phosphorus=None, potassium=None, organic_matter=None):
        if ph is not None:
            self.ph_level = ph
        if nitrogen is not None:
            self.nitrogen_level = nitrogen
        if phosphorus is not None:
            self.phosphorus_level = phosphorus
        if potassium is not None:
            self.potassium_level = potassium
        if organic_matter is not None:
            self.organic_matter = organic_matter