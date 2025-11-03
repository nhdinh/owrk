"""Initial procurement schema

Revision ID: 001
Revises:
Create Date: 2025-11-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create procurement_db schema if not exists
    op.execute("CREATE SCHEMA IF NOT EXISTS procurement_db")

    # Create vendors table
    op.create_table(
        'vendors',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vendor_code', sa.String(length=50), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('tax_code', sa.String(length=50), nullable=True),
        sa.Column('contact_person', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('rating', mysql.DECIMAL(precision=3, scale=2), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'BLACKLISTED', name='vendorstatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vendor_code'),
        schema='procurement_db'
    )
    op.create_index(op.f('ix_procurement_db_vendors_id'), 'vendors', ['id'], unique=False, schema='procurement_db')
    op.create_index(op.f('ix_procurement_db_vendors_vendor_code'), 'vendors', ['vendor_code'], unique=False, schema='procurement_db')

    # Create framework_contracts table
    op.create_table(
        'framework_contracts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contract_code', sa.String(length=50), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('contract_name', sa.String(length=255), nullable=False),
        sa.Column('contract_value', mysql.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('start_date', sa.DATE(), nullable=False),
        sa.Column('end_date', sa.DATE(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('terms_and_conditions', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'EXPIRED', 'TERMINATED', name='contractstatus'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['vendor_id'], ['procurement_db.vendors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contract_code'),
        schema='procurement_db'
    )
    op.create_index(op.f('ix_procurement_db_framework_contracts_id'), 'framework_contracts', ['id'], unique=False, schema='procurement_db')
    op.create_index(op.f('ix_procurement_db_framework_contracts_contract_code'), 'framework_contracts', ['contract_code'], unique=False, schema='procurement_db')

    # Create purchase_requests table
    op.create_table(
        'purchase_requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('request_code', sa.String(length=50), nullable=False),
        sa.Column('requested_by', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('request_date', sa.DATE(), nullable=False),
        sa.Column('required_date', sa.DATE(), nullable=True),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='priority'), nullable=False),
        sa.Column('procurement_type', sa.Enum('GOODS', 'SERVICES', 'BOTH', name='procurementtype'), nullable=False),
        sa.Column('justification', sa.Text(), nullable=True),
        sa.Column('budget_code', sa.String(length=50), nullable=True),
        sa.Column('estimated_total', mysql.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('approval_status', sa.Enum('DRAFT', 'PENDING', 'LEVEL1_APPROVED', 'LEVEL2_APPROVED', 'APPROVED', 'REJECTED', 'CANCELLED', name='approvalstatus'), nullable=False),
        sa.Column('level1_approved_by', sa.Integer(), nullable=True),
        sa.Column('level1_approved_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('level1_comments', sa.Text(), nullable=True),
        sa.Column('level2_approved_by', sa.Integer(), nullable=True),
        sa.Column('level2_approved_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('level2_comments', sa.Text(), nullable=True),
        sa.Column('level3_approved_by', sa.Integer(), nullable=True),
        sa.Column('level3_approved_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('level3_comments', sa.Text(), nullable=True),
        sa.Column('rejected_by', sa.Integer(), nullable=True),
        sa.Column('rejected_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('request_code'),
        schema='procurement_db'
    )
    op.create_index(op.f('ix_procurement_db_purchase_requests_id'), 'purchase_requests', ['id'], unique=False, schema='procurement_db')
    op.create_index(op.f('ix_procurement_db_purchase_requests_request_code'), 'purchase_requests', ['request_code'], unique=False, schema='procurement_db')
    op.create_index(op.f('ix_procurement_db_purchase_requests_approval_status'), 'purchase_requests', ['approval_status'], unique=False, schema='procurement_db')

    # Create purchase_request_items table
    op.create_table(
        'purchase_request_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('purchase_request_id', sa.Integer(), nullable=False),
        sa.Column('item_description', sa.Text(), nullable=False),
        sa.Column('specification', sa.Text(), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('estimated_unit_price', mysql.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('estimated_total_price', mysql.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['purchase_request_id'], ['procurement_db.purchase_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='procurement_db'
    )
    op.create_index(op.f('ix_procurement_db_purchase_request_items_id'), 'purchase_request_items', ['id'], unique=False, schema='procurement_db')
    op.create_index(op.f('ix_procurement_db_purchase_request_items_purchase_request_id'), 'purchase_request_items', ['purchase_request_id'], unique=False, schema='procurement_db')

    # Create quotations table
    op.create_table(
        'quotations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('quotation_code', sa.String(length=50), nullable=False),
        sa.Column('purchase_request_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('quotation_date', sa.DATE(), nullable=False),
        sa.Column('valid_until', sa.DATE(), nullable=True),
        sa.Column('total_amount', mysql.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('tax_amount', mysql.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('discount_amount', mysql.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('delivery_time', sa.String(length=100), nullable=True),
        sa.Column('payment_terms', sa.Text(), nullable=True),
        sa.Column('warranty_terms', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='quotationstatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['purchase_request_id'], ['procurement_db.purchase_requests.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['procurement_db.vendors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('quotation_code'),
        schema='procurement_db'
    )
    op.create_index(op.f('ix_procurement_db_quotations_id'), 'quotations', ['id'], unique=False, schema='procurement_db')
    op.create_index(op.f('ix_procurement_db_quotations_quotation_code'), 'quotations', ['quotation_code'], unique=False, schema='procurement_db')
    op.create_index(op.f('ix_procurement_db_quotations_vendor_id'), 'quotations', ['vendor_id'], unique=False, schema='procurement_db')

    # Create quotation_items table
    op.create_table(
        'quotation_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('quotation_id', sa.Integer(), nullable=False),
        sa.Column('purchase_request_item_id', sa.Integer(), nullable=True),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('product_description', sa.Text(), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', mysql.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('total_price', mysql.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['quotation_id'], ['procurement_db.quotations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['purchase_request_item_id'], ['procurement_db.purchase_request_items.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='procurement_db'
    )
    op.create_index(op.f('ix_procurement_db_quotation_items_id'), 'quotation_items', ['id'], unique=False, schema='procurement_db')
    op.create_index(op.f('ix_procurement_db_quotation_items_quotation_id'), 'quotation_items', ['quotation_id'], unique=False, schema='procurement_db')

    # Create purchase_orders table
    op.create_table(
        'purchase_orders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('order_code', sa.String(length=50), nullable=False),
        sa.Column('purchase_request_id', sa.Integer(), nullable=False),
        sa.Column('quotation_id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('order_date', sa.DATE(), nullable=False),
        sa.Column('expected_delivery_date', sa.DATE(), nullable=True),
        sa.Column('actual_delivery_date', sa.DATE(), nullable=True),
        sa.Column('subtotal', mysql.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('tax_amount', mysql.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('discount_amount', mysql.DECIMAL(precision=15, scale=2), nullable=True),
        sa.Column('total_amount', mysql.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('delivery_address', sa.Text(), nullable=True),
        sa.Column('delivery_contact', sa.String(length=255), nullable=True),
        sa.Column('delivery_phone', sa.String(length=50), nullable=True),
        sa.Column('payment_terms', sa.Text(), nullable=True),
        sa.Column('payment_status', sa.Enum('PENDING', 'PARTIAL', 'PAID', name='paymentstatus'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'COMPLETED', name='orderstatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['purchase_request_id'], ['procurement_db.purchase_requests.id'], ),
        sa.ForeignKeyConstraint(['quotation_id'], ['procurement_db.quotations.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['procurement_db.vendors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_code'),
        schema='procurement_db'
    )
    op.create_index(op.f('ix_procurement_db_purchase_orders_id'), 'purchase_orders', ['id'], unique=False, schema='procurement_db')
    op.create_index(op.f('ix_procurement_db_purchase_orders_order_code'), 'purchase_orders', ['order_code'], unique=False, schema='procurement_db')
    op.create_index(op.f('ix_procurement_db_purchase_orders_order_date'), 'purchase_orders', ['order_date'], unique=False, schema='procurement_db')
    op.create_index(op.f('ix_procurement_db_purchase_orders_status'), 'purchase_orders', ['status'], unique=False, schema='procurement_db')
    op.create_index(op.f('ix_procurement_db_purchase_orders_vendor_id'), 'purchase_orders', ['vendor_id'], unique=False, schema='procurement_db')

    # Create purchase_order_items table
    op.create_table(
        'purchase_order_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('purchase_order_id', sa.Integer(), nullable=False),
        sa.Column('quotation_item_id', sa.Integer(), nullable=True),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('product_description', sa.Text(), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', mysql.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('total_price', mysql.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('received_quantity', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['procurement_db.purchase_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['quotation_item_id'], ['procurement_db.quotation_items.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        schema='procurement_db'
    )
    op.create_index(op.f('ix_procurement_db_purchase_order_items_id'), 'purchase_order_items', ['id'], unique=False, schema='procurement_db')
    op.create_index(op.f('ix_procurement_db_purchase_order_items_purchase_order_id'), 'purchase_order_items', ['purchase_order_id'], unique=False, schema='procurement_db')


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_index(op.f('ix_procurement_db_purchase_order_items_purchase_order_id'), table_name='purchase_order_items', schema='procurement_db')
    op.drop_index(op.f('ix_procurement_db_purchase_order_items_id'), table_name='purchase_order_items', schema='procurement_db')
    op.drop_table('purchase_order_items', schema='procurement_db')

    op.drop_index(op.f('ix_procurement_db_purchase_orders_vendor_id'), table_name='purchase_orders', schema='procurement_db')
    op.drop_index(op.f('ix_procurement_db_purchase_orders_status'), table_name='purchase_orders', schema='procurement_db')
    op.drop_index(op.f('ix_procurement_db_purchase_orders_order_date'), table_name='purchase_orders', schema='procurement_db')
    op.drop_index(op.f('ix_procurement_db_purchase_orders_order_code'), table_name='purchase_orders', schema='procurement_db')
    op.drop_index(op.f('ix_procurement_db_purchase_orders_id'), table_name='purchase_orders', schema='procurement_db')
    op.drop_table('purchase_orders', schema='procurement_db')

    op.drop_index(op.f('ix_procurement_db_quotation_items_quotation_id'), table_name='quotation_items', schema='procurement_db')
    op.drop_index(op.f('ix_procurement_db_quotation_items_id'), table_name='quotation_items', schema='procurement_db')
    op.drop_table('quotation_items', schema='procurement_db')

    op.drop_index(op.f('ix_procurement_db_quotations_vendor_id'), table_name='quotations', schema='procurement_db')
    op.drop_index(op.f('ix_procurement_db_quotations_quotation_code'), table_name='quotations', schema='procurement_db')
    op.drop_index(op.f('ix_procurement_db_quotations_id'), table_name='quotations', schema='procurement_db')
    op.drop_table('quotations', schema='procurement_db')

    op.drop_index(op.f('ix_procurement_db_purchase_request_items_purchase_request_id'), table_name='purchase_request_items', schema='procurement_db')
    op.drop_index(op.f('ix_procurement_db_purchase_request_items_id'), table_name='purchase_request_items', schema='procurement_db')
    op.drop_table('purchase_request_items', schema='procurement_db')

    op.drop_index(op.f('ix_procurement_db_purchase_requests_approval_status'), table_name='purchase_requests', schema='procurement_db')
    op.drop_index(op.f('ix_procurement_db_purchase_requests_request_code'), table_name='purchase_requests', schema='procurement_db')
    op.drop_index(op.f('ix_procurement_db_purchase_requests_id'), table_name='purchase_requests', schema='procurement_db')
    op.drop_table('purchase_requests', schema='procurement_db')

    op.drop_index(op.f('ix_procurement_db_framework_contracts_contract_code'), table_name='framework_contracts', schema='procurement_db')
    op.drop_index(op.f('ix_procurement_db_framework_contracts_id'), table_name='framework_contracts', schema='procurement_db')
    op.drop_table('framework_contracts', schema='procurement_db')

    op.drop_index(op.f('ix_procurement_db_vendors_vendor_code'), table_name='vendors', schema='procurement_db')
    op.drop_index(op.f('ix_procurement_db_vendors_id'), table_name='vendors', schema='procurement_db')
    op.drop_table('vendors', schema='procurement_db')

    # Drop schema
    op.execute("DROP SCHEMA IF EXISTS procurement_db")
