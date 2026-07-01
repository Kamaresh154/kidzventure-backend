import uuid
from datetime import date, datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.leave_request import LeaveRequest
from app.schemas.leave_request import LeaveRequestCreate, LeaveRequestReview


async def list_leaves(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    employee_id: uuid.UUID | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[LeaveRequest], int]:
    q = select(LeaveRequest).where(
        LeaveRequest.organization_id == org_id,
        LeaveRequest.deleted_at.is_(None),
    )
    if employee_id:
        q = q.where(LeaveRequest.employee_id == employee_id)
    if status:
        q = q.where(LeaveRequest.status == status)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (
        await db.execute(q.order_by(LeaveRequest.created_at.desc()).offset((page - 1) * page_size).limit(page_size))
    ).scalars().all()
    return list(items), total


async def create_leave(db: AsyncSession, org_id: uuid.UUID, data: LeaveRequestCreate) -> LeaveRequest:
    leave = LeaveRequest(organization_id=org_id, **data.model_dump())
    db.add(leave)
    await db.commit()
    await db.refresh(leave)
    return leave


async def review_leave(
    db: AsyncSession, org_id: uuid.UUID, leave_id: uuid.UUID, data: LeaveRequestReview
) -> LeaveRequest:
    leave = await _get_leave(db, org_id, leave_id)
    if leave.status != "pending":
        raise HTTPException(status_code=400, detail="Leave already reviewed")
    leave.status = data.status
    leave.reviewed_by = data.reviewed_by
    leave.reviewed_on = date.today()
    leave.review_note = data.review_note
    await db.commit()
    await db.refresh(leave)
    return leave


async def get_leave_balance(db: AsyncSession, org_id: uuid.UUID, employee_id: uuid.UUID, year: int = 0) -> dict:
    if year == 0:
        year = date.today().year
    year_str = str(year)
    q = select(LeaveRequest).where(
        LeaveRequest.organization_id == org_id,
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status == "approved",
        LeaveRequest.deleted_at.is_(None),
    )
    leaves = (await db.execute(q)).scalars().all()
    used = {"casual": 0, "sick": 0, "earned": 0, "unpaid": 0, "other": 0}
    for lv in leaves:
        if lv.from_date.year == year:
            used[lv.leave_type] = used.get(lv.leave_type, 0) + lv.days
    quota = {"casual": 12, "sick": 12, "earned": 15, "unpaid": 999, "other": 5}
    remaining = {k: max(0, v - used.get(k, 0)) for k, v in quota.items()}
    return {"used": used, "quota": quota, "remaining": remaining}


async def _get_leave(db: AsyncSession, org_id: uuid.UUID, leave_id: uuid.UUID) -> LeaveRequest:
    result = await db.execute(
        select(LeaveRequest).where(
            LeaveRequest.id == leave_id,
            LeaveRequest.organization_id == org_id,
            LeaveRequest.deleted_at.is_(None),
        )
    )
    lv = result.scalar_one_or_none()
    if not lv:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return lv
