"""add is_system_role to roles table

Revision ID: 005
Revises: 004
Create Date: 2025-10-20

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    # Add is_system_role column to roles table
    op.add_column(
        "roles",
        sa.Column("is_system_role", sa.Boolean(), nullable=False, server_default="0"),
        schema="auth_db",
    )


def downgrade():
    # Remove is_system_role column
    op.drop_column("roles", "is_system_role", schema="auth_db")
