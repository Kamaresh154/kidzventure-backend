import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.types import UuidType


class LeaveRequest(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "leave_requests"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UuidType, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UuidType, ForeignKey("staff_profiles.id", ondelete="CASCADE"), nullable=False
    )
    employee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    leave_type: Mapped[str] = mapped_column(String(32), nullable=False)  # casual | sick | earned | unpaid | other
    from_date: Mapped[date] = mapped_column(Date, nullable=False)
    to_date: Mapped[date] = mapped_column(Date, nullable=False)
    days: Mapped[int] = mapped_column(nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)  # pending | approved | rejected
    reviewed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
