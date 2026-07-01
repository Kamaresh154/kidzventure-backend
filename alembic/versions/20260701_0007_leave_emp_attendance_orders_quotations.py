"""Add leave_requests, emp_attendance, orders, quotations tables.

Revision ID: 20260701_0007
Revises: 20260610_0006
Create Date: 2026-07-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260701_0007"
down_revision = "20260610_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # leave_requests
    op.create_table(
        "leave_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", sa.Uuid(), sa.ForeignKey("staff_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_name", sa.String(255), nullable=False),
        sa.Column("leave_type", sa.String(32), nullable=False),
        sa.Column("from_date", sa.Date(), nullable=False),
        sa.Column("to_date", sa.Date(), nullable=False),
        sa.Column("days", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("reviewed_by", sa.String(255), nullable=True),
        sa.Column("reviewed_on", sa.Date(), nullable=True),
        sa.Column("review_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # emp_attendance
    op.create_table(
        "emp_attendance",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", sa.Uuid(), sa.ForeignKey("staff_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_name", sa.String(255), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("check_in", sa.String(16), nullable=False),
        sa.Column("check_out", sa.String(16), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="present"),
        sa.Column("recorded_by", sa.String(255), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # orders
    op.create_table(
        "orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_no", sa.String(64), nullable=False),
        sa.Column("customer", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("subtotal", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("discount", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("total", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("payment_method", sa.String(32), nullable=True),
        sa.Column("payment_ref", sa.String(128), nullable=True),
        sa.Column("payment_status", sa.String(32), nullable=False, server_default="unpaid"),
        sa.Column("upi_ref_submitted", sa.String(128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("placed_by", sa.String(255), nullable=False),
        sa.Column("placed_by_role", sa.String(32), nullable=False, server_default="franchise"),
        sa.Column("assigned_to", sa.String(255), nullable=True),
        sa.Column("purchase_employee", sa.String(255), nullable=True),
        sa.Column("status_history", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # order_lines
    op.create_table(
        "order_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.String(64), nullable=False),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 2), nullable=False),
        sa.Column("total", sa.Numeric(18, 2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # quotations
    op.create_table(
        "quotations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quote_no", sa.String(64), nullable=False),
        sa.Column("customer_name", sa.String(255), nullable=False),
        sa.Column("customer_phone", sa.String(32), nullable=True),
        sa.Column("customer_email", sa.String(255), nullable=True),
        sa.Column("subtotal", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False, server_default="18"),
        sa.Column("tax_amount", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("total", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column("created_at_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # quotation_lines
    op.create_table(
        "quotation_lines",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("quotation_id", sa.Uuid(), sa.ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.String(64), nullable=False),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("sku", sa.String(100), nullable=True),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(18, 2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("quotation_lines")
    op.drop_table("quotations")
    op.drop_table("order_lines")
    op.drop_table("orders")
    op.drop_table("emp_attendance")
    op.drop_table("leave_requests")
