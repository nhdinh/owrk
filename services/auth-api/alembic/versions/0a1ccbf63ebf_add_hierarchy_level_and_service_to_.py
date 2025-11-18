"""add_hierarchy_level_and_service_to_roles_permissions

Revision ID: 0a1ccbf63ebf
Revises: ff1318f930c5
Create Date: 2025-11-18 07:33:44.163935

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a1ccbf63ebf'
down_revision: Union[str, None] = 'ff1318f930c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add hierarchy_level to roles table
    op.add_column(
        'roles',
        sa.Column('hierarchy_level', sa.Integer(), nullable=False, server_default='10'),
        schema='auth_db'
    )

    # Add service column to permissions table
    op.add_column(
        'permissions',
        sa.Column('service', sa.String(50), nullable=True),
        schema='auth_db'
    )

    # Update existing system roles with hierarchy levels
    op.execute("""
        UPDATE auth_db.roles
        SET hierarchy_level = CASE
            WHEN name = 'super_admin' THEN 100
            WHEN name = 'admin' THEN 90
            WHEN name = 'manager' THEN 50
            WHEN name = 'user' THEN 10
            ELSE 10
        END
        WHERE is_system_role = TRUE
    """)


def downgrade() -> None:
    # Remove hierarchy_level from roles table
    op.drop_column('roles', 'hierarchy_level', schema='auth_db')

    # Remove service from permissions table
    op.drop_column('permissions', 'service', schema='auth_db')
