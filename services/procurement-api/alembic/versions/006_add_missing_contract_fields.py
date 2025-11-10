"""add_missing_contract_fields

Revision ID: 006
Revises: 005
Create Date: 2025-11-08 01:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to framework_contracts table
    op.add_column('framework_contracts',
                  sa.Column('payment_terms', sa.Text(), nullable=True),
                  schema='procurement_db')
    op.add_column('framework_contracts',
                  sa.Column('delivery_terms', sa.Text(), nullable=True),
                  schema='procurement_db')
    op.add_column('framework_contracts',
                  sa.Column('contract_file_url', sa.String(length=500), nullable=True),
                  schema='procurement_db')

    # Remove unused description column (if exists)
    try:
        op.drop_column('framework_contracts', 'description', schema='procurement_db')
    except Exception:
        pass  # Column might not exist


def downgrade():
    # Remove added columns
    op.drop_column('framework_contracts', 'contract_file_url', schema='procurement_db')
    op.drop_column('framework_contracts', 'delivery_terms', schema='procurement_db')
    op.drop_column('framework_contracts', 'payment_terms', schema='procurement_db')

    # Re-add description column
    op.add_column('framework_contracts',
                  sa.Column('description', sa.Text(), nullable=True),
                  schema='procurement_db')
