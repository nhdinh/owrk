"""align_purchase_request_fields

Revision ID: 003
Revises: 002
Create Date: 2025-11-03 01:20:00

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Align purchase_requests and purchase_request_items fields with models"""

    # Fix purchase_requests table
    # Rename comment fields to notes fields
    op.alter_column(
        "purchase_requests",
        "level1_comments",
        new_column_name="level1_notes",
        existing_type=sa.Text(),
        schema="procurement_db",
    )
    op.alter_column(
        "purchase_requests",
        "level2_comments",
        new_column_name="level2_notes",
        existing_type=sa.Text(),
        schema="procurement_db",
    )
    op.alter_column(
        "purchase_requests",
        "level3_comments",
        new_column_name="level3_notes",
        existing_type=sa.Text(),
        schema="procurement_db",
    )

    # Add missing fields to purchase_requests
    op.add_column(
        "purchase_requests",
        sa.Column("title", sa.String(length=255), nullable=False, server_default=""),
        schema="procurement_db",
    )
    op.add_column(
        "purchase_requests",
        sa.Column("description", sa.Text(), nullable=True),
        schema="procurement_db",
    )
    op.add_column(
        "purchase_requests",
        sa.Column("expected_delivery_date", sa.DATE(), nullable=True),
        schema="procurement_db",
    )
    op.add_column(
        "purchase_requests",
        sa.Column("framework_contract_id", sa.Integer(), nullable=True),
        schema="procurement_db",
    )
    op.add_column(
        "purchase_requests",
        sa.Column("deleted_at", sa.TIMESTAMP(), nullable=True),
        schema="procurement_db",
    )

    # Add foreign key for framework_contract_id
    op.create_foreign_key(
        "fk_purchase_requests_framework_contract",
        "purchase_requests",
        "framework_contracts",
        ["framework_contract_id"],
        ["id"],
        source_schema="procurement_db",
        referent_schema="procurement_db",
    )

    # Fix purchase_request_items table
    # Rename item_description to product_name
    op.alter_column(
        "purchase_request_items",
        "item_description",
        new_column_name="product_name",
        existing_type=sa.Text(),
        schema="procurement_db",
    )

    # Rename estimated_total_price to estimated_total
    op.alter_column(
        "purchase_request_items",
        "estimated_total_price",
        new_column_name="estimated_total",
        existing_type=sa.DECIMAL(precision=15, scale=2),
        schema="procurement_db",
    )

    # Rename notes to reason
    op.alter_column(
        "purchase_request_items",
        "notes",
        new_column_name="reason",
        existing_type=sa.Text(),
        schema="procurement_db",
    )

    # Add product_description column
    op.add_column(
        "purchase_request_items",
        sa.Column("product_description", sa.Text(), nullable=True),
        schema="procurement_db",
    )

    # Add updated_at column
    op.add_column(
        "purchase_request_items",
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        schema="procurement_db",
    )


def downgrade() -> None:
    """Revert field name changes"""

    # Revert purchase_request_items changes
    op.drop_column("purchase_request_items", "updated_at", schema="procurement_db")
    op.drop_column(
        "purchase_request_items", "product_description", schema="procurement_db"
    )
    op.alter_column(
        "purchase_request_items",
        "reason",
        new_column_name="notes",
        existing_type=sa.Text(),
        schema="procurement_db",
    )
    op.alter_column(
        "purchase_request_items",
        "estimated_total",
        new_column_name="estimated_total_price",
        existing_type=sa.DECIMAL(precision=15, scale=2),
        schema="procurement_db",
    )
    op.alter_column(
        "purchase_request_items",
        "product_name",
        new_column_name="item_description",
        existing_type=sa.Text(),
        schema="procurement_db",
    )

    # Revert purchase_requests changes
    op.drop_constraint(
        "fk_purchase_requests_framework_contract",
        "purchase_requests",
        type_="foreignkey",
        schema="procurement_db",
    )
    op.drop_column("purchase_requests", "deleted_at", schema="procurement_db")
    op.drop_column(
        "purchase_requests", "framework_contract_id", schema="procurement_db"
    )
    op.drop_column(
        "purchase_requests", "expected_delivery_date", schema="procurement_db"
    )
    op.drop_column("purchase_requests", "description", schema="procurement_db")
    op.drop_column("purchase_requests", "title", schema="procurement_db")
    op.alter_column(
        "purchase_requests",
        "level3_notes",
        new_column_name="level3_comments",
        existing_type=sa.Text(),
        schema="procurement_db",
    )
    op.alter_column(
        "purchase_requests",
        "level2_notes",
        new_column_name="level2_comments",
        existing_type=sa.Text(),
        schema="procurement_db",
    )
    op.alter_column(
        "purchase_requests",
        "level1_notes",
        new_column_name="level1_comments",
        existing_type=sa.Text(),
        schema="procurement_db",
    )
