import uuid
from datetime import date, datetime, timezone

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.emp_attendance import EmployeeAttendance
from app.schemas.emp_attendance import EmpAttendanceCreate, EmpAttendanceCheckOut


async def list_attendance(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    employee_id: uuid.UUID | None = None,
    on_date: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[EmployeeAttendance], int]:
    q = select(EmployeeAttendance).where(EmployeeAttendance.organization_id == org_id)
    if employee_id:
        q = q.where(EmployeeAttendance.employee_id == employee_id)
    if on_date:
        q = q.where(EmployeeAttendance.date == on_date)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (
        await db.execute(q.order_by(EmployeeAttendance.recorded_at.desc()).offset((page - 1) * page_size).limit(page_size))
    ).scalars().all()
    return list(items), total


async def check_in(db: AsyncSession, org_id: uuid.UUID, data: EmpAttendanceCreate) -> EmployeeAttendance:
    existing = await _get_today_record(db, org_id, data.employee_id, data.date)
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in today")
    record = EmployeeAttendance(
        organization_id=org_id,
        employee_id=data.employee_id,
        employee_name=data.employee_name,
        date=data.date,
        check_in=data.check_in,
        status=data.status,
        recorded_at=datetime.now(timezone.utc),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def check_out(
    db: AsyncSession, org_id: uuid.UUID, employee_id: uuid.UUID, date_str: date, data: EmpAttendanceCheckOut
) -> EmployeeAttendance:
    record = await _get_today_record(db, org_id, employee_id, date_str)
    if not record:
        raise HTTPException(status_code=404, detail="No check-in record found for today")
    if record.check_out:
        raise HTTPException(status_code=400, detail="Already checked out")
    record.check_out = data.check_out
    await db.commit()
    await db.refresh(record)
    return record


async def get_today_status(db: AsyncSession, org_id: uuid.UUID, employee_id: uuid.UUID) -> EmployeeAttendance | None:
    today = date.today()
    return await _get_today_record(db, org_id, employee_id, today)


async def _get_today_record(
    db: AsyncSession, org_id: uuid.UUID, employee_id: uuid.UUID, on_date: date
) -> EmployeeAttendance | None:
    result = await db.execute(
        select(EmployeeAttendance).where(
            EmployeeAttendance.organization_id == org_id,
            EmployeeAttendance.employee_id == employee_id,
            EmployeeAttendance.date == on_date,
        )
    )
    return result.scalar_one_or_none()
