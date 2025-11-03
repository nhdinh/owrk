"""increase qr_code column size

Revision ID: 32a6f5a3e6b6
Revises:
Create Date: 2025-11-02 07:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32a6f5a3e6b6'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Increase qr_code column from VARCHAR(500) to TEXT
    op.alter_column('assets', 'qr_code',
                    existing_type=sa.String(500),
                    type_=sa.Text(),
                    existing_nullable=True,
                    schema='asset_db')


def downgrade() -> None:
    # Revert back to VARCHAR(500)
    op.alter_column('assets', 'qr_code',
                    existing_type=sa.Text(),
                    type_=sa.String(500),
                    existing_nullable=True,
                    schema='asset_db')
