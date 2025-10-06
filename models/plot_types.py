from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, declared_attr
from datetime import datetime
import uuid

from models.runner import Base


class PlotTypeBase(Base):
    """Base class for all plot type models with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    plot_id = Column(String(36), ForeignKey('plots.uuid'), nullable=False)
    name = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Note: No direct relationship to avoid SQLAlchemy complexity with abstract base classes
    # Plot type data is accessed via queries in the controller
    
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "plot_id": self.plot_id,
            "name": self.name,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "type": self.__class__.__name__.lower().replace('plottype', '')
        }


class FieldPlotType(PlotTypeBase):
    """Field plot type for crop cultivation"""
    __tablename__ = "field_plot_types"
    
    crop_type = Column(String(100), nullable=True)
    soil_type = Column(String(100), nullable=True)
    irrigation_system = Column(String(100), nullable=True)
    fertilizer_schedule = Column(Text, nullable=True)
    harvest_season = Column(String(50), nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "crop_type": self.crop_type,
            "soil_type": self.soil_type,
            "irrigation_system": self.irrigation_system,
            "fertilizer_schedule": self.fertilizer_schedule,
            "harvest_season": self.harvest_season
        })
        return base_dict


class BarnPlotType(PlotTypeBase):
    """Barn plot type for equipment and livestock shelter"""
    __tablename__ = "barn_plot_types"
    
    capacity = Column(Integer, nullable=True)
    equipment_stored = Column(Text, nullable=True)
    ventilation_system = Column(String(100), nullable=True)
    electricity_available = Column(String(20), nullable=True)
    water_access = Column(String(20), nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "capacity": self.capacity,
            "equipment_stored": self.equipment_stored,
            "ventilation_system": self.ventilation_system,
            "electricity_available": self.electricity_available,
            "water_access": self.water_access
        })
        return base_dict


class PasturePlotType(PlotTypeBase):
    """Pasture plot type for livestock grazing"""
    __tablename__ = "pasture_plot_types"
    
    grass_type = Column(String(100), nullable=True)
    livestock_capacity = Column(Integer, nullable=True)
    fencing_type = Column(String(100), nullable=True)
    water_source = Column(String(100), nullable=True)
    grazing_season = Column(String(50), nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "grass_type": self.grass_type,
            "livestock_capacity": self.livestock_capacity,
            "fencing_type": self.fencing_type,
            "water_source": self.water_source,
            "grazing_season": self.grazing_season
        })
        return base_dict


class GreenhousePlotType(PlotTypeBase):
    """Greenhouse plot type for controlled environment cultivation"""
    __tablename__ = "greenhouse_plot_types"
    
    climate_control = Column(String(100), nullable=True)
    heating_system = Column(String(100), nullable=True)
    cooling_system = Column(String(100), nullable=True)
    humidity_control = Column(String(100), nullable=True)
    growing_medium = Column(String(100), nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "climate_control": self.climate_control,
            "heating_system": self.heating_system,
            "cooling_system": self.cooling_system,
            "humidity_control": self.humidity_control,
            "growing_medium": self.growing_medium
        })
        return base_dict


class ChickenPenPlotType(PlotTypeBase):
    """Chicken pen plot type for poultry farming"""
    __tablename__ = "chicken_pen_plot_types"
    
    chicken_capacity = Column(Integer, nullable=True)
    coop_type = Column(String(100), nullable=True)
    nesting_boxes = Column(Integer, nullable=True)
    run_area_covered = Column(String(20), nullable=True)
    feeding_system = Column(String(100), nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "chicken_capacity": self.chicken_capacity,
            "coop_type": self.coop_type,
            "nesting_boxes": self.nesting_boxes,
            "run_area_covered": self.run_area_covered,
            "feeding_system": self.feeding_system
        })
        return base_dict


class CowShedPlotType(PlotTypeBase):
    """Cow shed plot type for cattle housing"""
    __tablename__ = "cow_shed_plot_types"
    
    cow_capacity = Column(Integer, nullable=True)
    milking_system = Column(String(100), nullable=True)
    feeding_system = Column(String(100), nullable=True)
    bedding_type = Column(String(100), nullable=True)
    waste_management = Column(String(100), nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "cow_capacity": self.cow_capacity,
            "milking_system": self.milking_system,
            "feeding_system": self.feeding_system,
            "bedding_type": self.bedding_type,
            "waste_management": self.waste_management
        })
        return base_dict


class FishPondPlotType(PlotTypeBase):
    """Fish pond plot type for aquaculture"""
    __tablename__ = "fish_pond_plot_types"
    
    pond_depth = Column(String(50), nullable=True)
    fish_species = Column(String(100), nullable=True)
    water_source = Column(String(100), nullable=True)
    filtration_system = Column(String(100), nullable=True)
    aeration_system = Column(String(100), nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "pond_depth": self.pond_depth,
            "fish_species": self.fish_species,
            "water_source": self.water_source,
            "filtration_system": self.filtration_system,
            "aeration_system": self.aeration_system
        })
        return base_dict


class ResidencePlotType(PlotTypeBase):
    """Residence plot type for housing"""
    __tablename__ = "residence_plot_types"
    
    building_type = Column(String(100), nullable=True)
    occupancy = Column(Integer, nullable=True)
    utilities = Column(Text, nullable=True)
    garden_area = Column(String(50), nullable=True)
    parking_spaces = Column(Integer, nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "building_type": self.building_type,
            "occupancy": self.occupancy,
            "utilities": self.utilities,
            "garden_area": self.garden_area,
            "parking_spaces": self.parking_spaces
        })
        return base_dict


class NaturalAreaPlotType(PlotTypeBase):
    """Natural area plot type for conservation"""
    __tablename__ = "natural_area_plot_types"
    
    ecosystem_type = Column(String(100), nullable=True)
    conservation_status = Column(String(100), nullable=True)
    wildlife_present = Column(Text, nullable=True)
    management_plan = Column(Text, nullable=True)
    access_restrictions = Column(Text, nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "ecosystem_type": self.ecosystem_type,
            "conservation_status": self.conservation_status,
            "wildlife_present": self.wildlife_present,
            "management_plan": self.management_plan,
            "access_restrictions": self.access_restrictions
        })
        return base_dict


class WaterSourcePlotType(PlotTypeBase):
    """Water source plot type for wells, springs, etc."""
    __tablename__ = "water_source_plot_types"
    
    source_type = Column(String(100), nullable=True)
    water_quality = Column(String(100), nullable=True)
    flow_rate = Column(String(50), nullable=True)
    depth = Column(String(50), nullable=True)
    treatment_required = Column(String(20), nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "source_type": self.source_type,
            "water_quality": self.water_quality,
            "flow_rate": self.flow_rate,
            "depth": self.depth,
            "treatment_required": self.treatment_required
        })
        return base_dict


# Mapping of plot type enum values to model classes
PLOT_TYPE_MODELS = {
    "field": FieldPlotType,
    "barn": BarnPlotType,
    "pasture": PasturePlotType,
    "green-house": GreenhousePlotType,
    "chicken-pen": ChickenPenPlotType,
    "cow-shed": CowShedPlotType,
    "fish-pond": FishPondPlotType,
    "residence": ResidencePlotType,
    "natural-area": NaturalAreaPlotType,
    "water-source": WaterSourcePlotType
}