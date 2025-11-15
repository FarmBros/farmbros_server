"""create farm table - using geometry instead

Revision ID: 8d56ccc0eacd
Revises: 910f6b8b5774
Create Date: 2025-08-21 16:59:59.802658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '8d56ccc0eacd'
down_revision: Union[str, Sequence[str], None] = '910f6b8b5774'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the farms table without spatial columns first
    op.create_table('farms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('owner_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('area_sqm', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.uuid'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid')
    )

    # Add spatial columns using raw SQL for MySQL/MariaDB
    op.execute(text("ALTER TABLE farms ADD COLUMN boundary POLYGON NOT NULL"))
    op.execute(text("ALTER TABLE farms ADD COLUMN centroid POINT"))

    # Create spatial indexes
    op.execute(text("CREATE SPATIAL INDEX idx_farms_boundary ON farms(boundary) NOT NULL"))
    op.execute(text("CREATE SPATIAL INDEX idx_farms_centroid ON farms(centroid) NOT NULL"))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('farms')