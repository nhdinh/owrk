"""add device_name to refresh_tokens

Revision ID: 003
Revises: 002
Create Date: 2025-10-20

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add device_name column to refresh_tokens table
    op.add_column(
        'refresh_tokens',
        sa.Column('device_name', sa.String(100), nullable=True),
        schema='auth_db'
    )


def downgrade():
    # Remove device_name column
    op.drop_column('refresh_tokens', 'device_name', schema='auth_db')
