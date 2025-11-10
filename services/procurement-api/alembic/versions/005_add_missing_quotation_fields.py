"""add_missing_quotation_fields

Revision ID: 005
Revises: 004
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to quotations table
    op.add_column('quotations',
                  sa.Column('final_amount', mysql.DECIMAL(precision=15, scale=2), nullable=False, server_default='0.00'),
                  schema='procurement_db')
    op.add_column('quotations',
                  sa.Column('delivery_terms', sa.Text(), nullable=True),
                  schema='procurement_db')
    op.add_column('quotations',
                  sa.Column('quotation_file_url', sa.String(length=500), nullable=True),
                  schema='procurement_db')
    op.add_column('quotations',
                  sa.Column('accepted_by', sa.Integer(), nullable=True),
                  schema='procurement_db')
    op.add_column('quotations',
                  sa.Column('accepted_at', sa.TIMESTAMP(), nullable=True),
                  schema='procurement_db')
    op.add_column('quotations',
                  sa.Column('rejected_by', sa.Integer(), nullable=True),
                  schema='procurement_db')
    op.add_column('quotations',
                  sa.Column('rejected_at', sa.TIMESTAMP(), nullable=True),
                  schema='procurement_db')
    op.add_column('quotations',
                  sa.Column('rejection_reason', sa.Text(), nullable=True),
                  schema='procurement_db')

    # Drop the server_default after adding the column (so existing rows get 0.00, but new rows require explicit value)
    op.alter_column('quotations', 'final_amount',
                    existing_type=mysql.DECIMAL(precision=15, scale=2),
                    server_default=None,
                    schema='procurement_db')


def downgrade():
    # Remove added columns
    op.drop_column('quotations', 'rejection_reason', schema='procurement_db')
    op.drop_column('quotations', 'rejected_at', schema='procurement_db')
    op.drop_column('quotations', 'rejected_by', schema='procurement_db')
    op.drop_column('quotations', 'accepted_at', schema='procurement_db')
    op.drop_column('quotations', 'accepted_by', schema='procurement_db')
    op.drop_column('quotations', 'quotation_file_url', schema='procurement_db')
    op.drop_column('quotations', 'delivery_terms', schema='procurement_db')
    op.drop_column('quotations', 'final_amount', schema='procurement_db')
