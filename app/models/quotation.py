import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.types import JsonType, UuidType


class Quotation(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "quotations"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UuidType, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    quote_no: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=18, nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)  # draft | sent | accepted | rejected
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at_date: Mapped[date | None] = mapped_column(nullable=True)

    lines: Mapped[list["QuotationLine"]] = relationship(back_populates="quotation", cascade="all, delete-orphan")


class QuotationLine(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "quotation_lines"

    quotation_id: Mapped[uuid.UUID] = mapped_column(
        UuidType, ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(String(64), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str | None] = mapped_column(String(100), nullable=True)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    quotation: Mapped["Quotation"] = relationship(back_populates="lines")
