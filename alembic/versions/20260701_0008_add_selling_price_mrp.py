"""Add selling_price and mrp columns to inventory_products.

Revision ID: 20260701_0008
Revises: 20260701_0007
Create Date: 2026-07-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260701_0008"
down_revision = "20260701_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("inventory_products", sa.Column("selling_price", sa.Numeric(14, 2), nullable=False, server_default=sa.text("0")))
    op.add_column("inventory_products", sa.Column("mrp", sa.Numeric(14, 2), nullable=False, server_default=sa.text("0")))


def downgrade() -> None:
    op.drop_column("inventory_products", "mrp")
    op.drop_column("inventory_products", "selling_price")
