"""Add plot types tables

Revision ID: 8fd931069047
Revises: 51357963ae67
Create Date: 2025-10-06 22:17:50.838163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fd931069047'
down_revision: Union[str, Sequence[str], None] = '51357963ae67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create field plot types table
    op.create_table('field_plot_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('plot_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('crop_type', sa.String(length=100), nullable=True),
        sa.Column('soil_type', sa.String(length=100), nullable=True),
        sa.Column('irrigation_system', sa.String(length=100), nullable=True),
        sa.Column('fertilizer_schedule', sa.Text(), nullable=True),
        sa.Column('harvest_season', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.uuid'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_field_plot_types_uuid'), 'field_plot_types', ['uuid'], unique=True)

    # Create barn plot types table
    op.create_table('barn_plot_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('plot_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('equipment_stored', sa.Text(), nullable=True),
        sa.Column('ventilation_system', sa.String(length=100), nullable=True),
        sa.Column('electricity_available', sa.String(length=20), nullable=True),
        sa.Column('water_access', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.uuid'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_barn_plot_types_uuid'), 'barn_plot_types', ['uuid'], unique=True)

    # Create pasture plot types table
    op.create_table('pasture_plot_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('plot_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('grass_type', sa.String(length=100), nullable=True),
        sa.Column('livestock_capacity', sa.Integer(), nullable=True),
        sa.Column('fencing_type', sa.String(length=100), nullable=True),
        sa.Column('water_source', sa.String(length=100), nullable=True),
        sa.Column('grazing_season', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.uuid'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pasture_plot_types_uuid'), 'pasture_plot_types', ['uuid'], unique=True)

    # Create greenhouse plot types table
    op.create_table('greenhouse_plot_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('plot_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('climate_control', sa.String(length=100), nullable=True),
        sa.Column('heating_system', sa.String(length=100), nullable=True),
        sa.Column('cooling_system', sa.String(length=100), nullable=True),
        sa.Column('humidity_control', sa.String(length=100), nullable=True),
        sa.Column('growing_medium', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.uuid'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_greenhouse_plot_types_uuid'), 'greenhouse_plot_types', ['uuid'], unique=True)

    # Create chicken pen plot types table
    op.create_table('chicken_pen_plot_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('plot_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('chicken_capacity', sa.Integer(), nullable=True),
        sa.Column('coop_type', sa.String(length=100), nullable=True),
        sa.Column('nesting_boxes', sa.Integer(), nullable=True),
        sa.Column('run_area_covered', sa.String(length=20), nullable=True),
        sa.Column('feeding_system', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.uuid'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chicken_pen_plot_types_uuid'), 'chicken_pen_plot_types', ['uuid'], unique=True)

    # Create cow shed plot types table
    op.create_table('cow_shed_plot_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('plot_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('cow_capacity', sa.Integer(), nullable=True),
        sa.Column('milking_system', sa.String(length=100), nullable=True),
        sa.Column('feeding_system', sa.String(length=100), nullable=True),
        sa.Column('bedding_type', sa.String(length=100), nullable=True),
        sa.Column('waste_management', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.uuid'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cow_shed_plot_types_uuid'), 'cow_shed_plot_types', ['uuid'], unique=True)

    # Create fish pond plot types table
    op.create_table('fish_pond_plot_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('plot_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('pond_depth', sa.String(length=50), nullable=True),
        sa.Column('fish_species', sa.String(length=100), nullable=True),
        sa.Column('water_source', sa.String(length=100), nullable=True),
        sa.Column('filtration_system', sa.String(length=100), nullable=True),
        sa.Column('aeration_system', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.uuid'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fish_pond_plot_types_uuid'), 'fish_pond_plot_types', ['uuid'], unique=True)

    # Create residence plot types table
    op.create_table('residence_plot_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('plot_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('building_type', sa.String(length=100), nullable=True),
        sa.Column('occupancy', sa.Integer(), nullable=True),
        sa.Column('utilities', sa.Text(), nullable=True),
        sa.Column('garden_area', sa.String(length=50), nullable=True),
        sa.Column('parking_spaces', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.uuid'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_residence_plot_types_uuid'), 'residence_plot_types', ['uuid'], unique=True)

    # Create natural area plot types table
    op.create_table('natural_area_plot_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('plot_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('ecosystem_type', sa.String(length=100), nullable=True),
        sa.Column('conservation_status', sa.String(length=100), nullable=True),
        sa.Column('wildlife_present', sa.Text(), nullable=True),
        sa.Column('management_plan', sa.Text(), nullable=True),
        sa.Column('access_restrictions', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.uuid'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_natural_area_plot_types_uuid'), 'natural_area_plot_types', ['uuid'], unique=True)

    # Create water source plot types table
    op.create_table('water_source_plot_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('plot_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('source_type', sa.String(length=100), nullable=True),
        sa.Column('water_quality', sa.String(length=100), nullable=True),
        sa.Column('flow_rate', sa.String(length=50), nullable=True),
        sa.Column('depth', sa.String(length=50), nullable=True),
        sa.Column('treatment_required', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.uuid'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_water_source_plot_types_uuid'), 'water_source_plot_types', ['uuid'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop all plot type tables in reverse order
    op.drop_index(op.f('ix_water_source_plot_types_uuid'), table_name='water_source_plot_types')
    op.drop_table('water_source_plot_types')
    
    op.drop_index(op.f('ix_natural_area_plot_types_uuid'), table_name='natural_area_plot_types')
    op.drop_table('natural_area_plot_types')
    
    op.drop_index(op.f('ix_residence_plot_types_uuid'), table_name='residence_plot_types')
    op.drop_table('residence_plot_types')
    
    op.drop_index(op.f('ix_fish_pond_plot_types_uuid'), table_name='fish_pond_plot_types')
    op.drop_table('fish_pond_plot_types')
    
    op.drop_index(op.f('ix_cow_shed_plot_types_uuid'), table_name='cow_shed_plot_types')
    op.drop_table('cow_shed_plot_types')
    
    op.drop_index(op.f('ix_chicken_pen_plot_types_uuid'), table_name='chicken_pen_plot_types')
    op.drop_table('chicken_pen_plot_types')
    
    op.drop_index(op.f('ix_greenhouse_plot_types_uuid'), table_name='greenhouse_plot_types')
    op.drop_table('greenhouse_plot_types')
    
    op.drop_index(op.f('ix_pasture_plot_types_uuid'), table_name='pasture_plot_types')
    op.drop_table('pasture_plot_types')
    
    op.drop_index(op.f('ix_barn_plot_types_uuid'), table_name='barn_plot_types')
    op.drop_table('barn_plot_types')
    
    op.drop_index(op.f('ix_field_plot_types_uuid'), table_name='field_plot_types')
    op.drop_table('field_plot_types')
