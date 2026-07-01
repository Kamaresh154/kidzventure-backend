import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin
from app.models.types import UuidType


class EmployeeAttendance(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "emp_attendance"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UuidType, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UuidType, ForeignKey("staff_profiles.id", ondelete="CASCADE"), nullable=False
    )
    employee_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    check_in: Mapped[str] = mapped_column(String(16), nullable=False)  # HH:MM format
    check_out: Mapped[str | None] = mapped_column(String(16), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="present", nullable=False)  # present | absent | half-day
    recorded_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
