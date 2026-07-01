from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class EmpAttendanceCreate(BaseModel):
    employee_id: UUID
    employee_name: str = Field(min_length=1, max_length=255)
    date: date
    check_in: str = Field(..., pattern=r"^\d{1,2}:\d{2}\s*(AM|PM)?$", description="Time in HH:MM format")
    status: str = Field(default="present", pattern="^(present|absent|half-day)$")


class EmpAttendanceCheckOut(BaseModel):
    check_out: str = Field(..., pattern=r"^\d{1,2}:\d{2}\s*(AM|PM)?$")


class EmpAttendanceResponse(ORMModel):
    id: UUID
    organization_id: UUID
    employee_id: UUID
    employee_name: str
    date: date
    check_in: str
    check_out: str | None
    status: str
    recorded_by: str | None
    recorded_at: object


class EmpAttendanceListResponse(BaseModel):
    items: list[EmpAttendanceResponse]
    total: int
    page: int
    page_size: int
