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
    
    soil_type = Column(String(100), nullable=True)
    irrigation_system = Column(String(100), nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "soil_type": self.soil_type,
            "irrigation_system": self.irrigation_system,
        })
        return base_dict


class BarnPlotType(PlotTypeBase):
    """Barn plot type for equipment and livestock shelter"""
    __tablename__ = "barn_plot_types"

    structure_type = Column(String(100), nullable=True)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "structure_type": self.structure_type,
        })
        return base_dict


class PasturePlotType(PlotTypeBase):
    """Pasture plot type for livestock grazing"""
    __tablename__ = "pasture_plot_types"

    status = Column(String(50), nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "status": self.status
        })
        return base_dict


class GreenhousePlotType(PlotTypeBase):
    """Greenhouse plot type for controlled environment cultivation"""
    __tablename__ = "greenhouse_plot_types"
    
    greenhouse_type = Column(String(100), nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "greenhouse_type": self.greenhouse_type,
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
    filtration_system = Column(String(100), nullable=True)
    aeration_system = Column(String(100), nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "pond_depth": self.pond_depth,
            "filtration_system": self.filtration_system,
            "aeration_system": self.aeration_system
        })
        return base_dict


class ResidencePlotType(PlotTypeBase):
    """Residence plot type for housing"""
    __tablename__ = "residence_plot_types"
    
    building_type = Column(String(100), nullable=True)
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "building_type": self.building_type
        })
        return base_dict


class NaturalAreaPlotType(PlotTypeBase):
    """Natural area plot type for conservation"""
    __tablename__ = "natural_area_plot_types"
    
    ecosystem_type = Column(String(100), nullable=True, default='Wild')
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "ecosystem_type": self.ecosystem_type,
        })
        return base_dict


class WaterSourcePlotType(PlotTypeBase):
    """Water source plot type for wells, springs, etc."""
    __tablename__ = "water_source_plot_types"
    
    source_type = Column(String(100), nullable=True)
    depth = Column(String(50), nullable=True)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "source_type": self.source_type,
            "depth": self.depth,
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