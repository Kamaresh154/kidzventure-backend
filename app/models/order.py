import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.types import JsonType, UuidType


class Order(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "orders"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UuidType, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    order_no: Mapped[str] = mapped_column(String(64), nullable=False)
    customer: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)  # pending | confirmed | dispatched | delivered | cancelled
    payment_method: Mapped[str | None] = mapped_column(String(32), nullable=True)  # gpay | cod | cash | pending
    payment_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payment_status: Mapped[str] = mapped_column(String(32), default="unpaid", nullable=False)  # unpaid | pending_verification | paid
    upi_ref_submitted: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    placed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    placed_by_role: Mapped[str] = mapped_column(String(32), default="franchise", nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purchase_employee: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status_history: Mapped[dict] = mapped_column(JsonType, default=list, nullable=False)

    lines: Mapped[list["OrderLine"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderLine(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "order_lines"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UuidType, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(String(64), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="lines")
