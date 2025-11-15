"""Added logintype enum

Revision ID: 634b2241e941
Revises: e235af1636a8
Create Date: 2025-08-28 18:41:57.284453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '634b2241e941'
down_revision: Union[str, Sequence[str], None] = 'e235af1636a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # First drop the column that depends on the enum
    try:
        op.drop_column('users', 'login_type')
    except:
        pass  # Column doesn't exist, continue
    
    # Now drop the enum type
    op.execute("DROP TYPE IF EXISTS logintype")
    
    # Create new enum type with correct values
    login_type_enum = sa.Enum('PASSWORD', 'GOOGLE_AUTH', 'BOTH', name='logintype')
    login_type_enum.create(op.get_bind())
    
    # Add login_type column to users table
    op.add_column('users', sa.Column('login_type', login_type_enum, nullable=False, server_default='PASSWORD'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove login_type column and enum
    op.drop_column('users', 'login_type')
    op.execute("DROP TYPE IF EXISTS logintype")