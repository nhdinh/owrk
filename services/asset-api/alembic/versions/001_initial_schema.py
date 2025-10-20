"""Initial schema for asset management

Revision ID: 001
Revises:
Create Date: 2025-01-18 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create schema
    op.execute('CREATE SCHEMA IF NOT EXISTS asset_db')

    # Create asset_categories table
    op.create_table(
        'asset_categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['parent_id'], ['asset_db.asset_categories.id'], name='fk_asset_categories_parent'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        schema='asset_db'
    )
    op.create_index('idx_asset_categories_code', 'asset_categories', ['code'], schema='asset_db')
    op.create_index('idx_asset_categories_parent_id', 'asset_categories', ['parent_id'], schema='asset_db')

    # Create assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset_code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('asset_type', sa.Enum('FIXED_ASSET', 'TOOL', name='assettype'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('manufacturer', sa.String(length=255), nullable=True),
        sa.Column('model', sa.String(length=255), nullable=True),
        sa.Column('serial_number', sa.String(length=255), nullable=True),
        sa.Column('purchase_price', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('purchase_date', sa.Date(), nullable=False),
        sa.Column('purchase_order_id', sa.Integer(), nullable=True),
        sa.Column('depreciation_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('depreciation_method', sa.Enum('STRAIGHT_LINE', 'DECLINING_BALANCE', name='depreciationmethod'), nullable=True),
        sa.Column('useful_life_months', sa.Integer(), nullable=True),
        sa.Column('residual_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('warranty_months', sa.Integer(), nullable=True),
        sa.Column('warranty_start_date', sa.Date(), nullable=True),
        sa.Column('warranty_end_date', sa.Date(), nullable=True),
        sa.Column('warranty_provider', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Enum('NEW', 'IN_USE', 'AVAILABLE', 'MAINTENANCE', 'BROKEN', 'DISPOSED', name='assetstatus'), nullable=False, server_default='NEW'),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('current_user_id', sa.Integer(), nullable=True),
        sa.Column('qr_code', sa.String(length=500), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['asset_db.asset_categories.id'], name='fk_assets_category'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_code'),
        schema='asset_db'
    )
    op.create_index('idx_assets_asset_code', 'assets', ['asset_code'], schema='asset_db')
    op.create_index('idx_assets_category_id', 'assets', ['category_id'], schema='asset_db')
    op.create_index('idx_assets_status', 'assets', ['status'], schema='asset_db')
    op.create_index('idx_assets_asset_type', 'assets', ['asset_type'], schema='asset_db')
    op.create_index('idx_assets_department_id', 'assets', ['department_id'], schema='asset_db')
    op.create_index('idx_assets_current_user_id', 'assets', ['current_user_id'], schema='asset_db')
    op.create_index('idx_assets_purchase_date', 'assets', ['purchase_date'], schema='asset_db')

    # Create asset_assignments table
    op.create_table(
        'asset_assignments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('assigned_date', sa.Date(), nullable=False),
        sa.Column('assigned_by', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('handover_document_url', sa.String(length=500), nullable=True),
        sa.Column('returned_date', sa.Date(), nullable=True),
        sa.Column('returned_by', sa.Integer(), nullable=True),
        sa.Column('return_condition', sa.Enum('GOOD', 'DAMAGED', 'BROKEN', name='returncondition'), nullable=True),
        sa.Column('return_notes', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'RETURNED', name='assignmentstatus'), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['asset_id'], ['asset_db.assets.id'], name='fk_asset_assignments_asset', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='asset_db'
    )
    op.create_index('idx_asset_assignments_asset_id', 'asset_assignments', ['asset_id'], schema='asset_db')
    op.create_index('idx_asset_assignments_user_id', 'asset_assignments', ['user_id'], schema='asset_db')
    op.create_index('idx_asset_assignments_status', 'asset_assignments', ['status'], schema='asset_db')
    op.create_index('idx_asset_assignments_assigned_date', 'asset_assignments', ['assigned_date'], schema='asset_db')

    # Create asset_attachments table
    op.create_table(
        'asset_attachments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.Enum('INVOICE', 'WARRANTY', 'PHOTO', 'DOCUMENT', name='filetype'), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['asset_id'], ['asset_db.assets.id'], name='fk_asset_attachments_asset', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='asset_db'
    )
    op.create_index('idx_asset_attachments_asset_id', 'asset_attachments', ['asset_id'], schema='asset_db')
    op.create_index('idx_asset_attachments_file_type', 'asset_attachments', ['file_type'], schema='asset_db')

    # Create asset_depreciation_records table
    op.create_table(
        'asset_depreciation_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('period_month', sa.Integer(), nullable=False),
        sa.Column('opening_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('depreciation_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('closing_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('accumulated_depreciation', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['asset_id'], ['asset_db.assets.id'], name='fk_asset_depreciation_asset', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_id', 'period_month', name='uk_asset_period'),
        schema='asset_db'
    )
    op.create_index('idx_asset_depreciation_asset_id', 'asset_depreciation_records', ['asset_id'], schema='asset_db')
    op.create_index('idx_asset_depreciation_period', 'asset_depreciation_records', ['period_month'], schema='asset_db')


def downgrade() -> None:
    # Drop tables
    op.drop_table('asset_depreciation_records', schema='asset_db')
    op.drop_table('asset_attachments', schema='asset_db')
    op.drop_table('asset_assignments', schema='asset_db')
    op.drop_table('assets', schema='asset_db')
    op.drop_table('asset_categories', schema='asset_db')

    # Drop schema
    op.execute('DROP SCHEMA IF EXISTS asset_db')
