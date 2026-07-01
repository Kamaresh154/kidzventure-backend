from uuid import UUID

from fastapi import APIRouter, Query

from app.core.deps import CurrentUserDep, DbSession
from app.schemas.leave_request import (
    LeaveListResponse, LeaveRequestCreate, LeaveRequestResponse, LeaveRequestReview,
)
from app.services import leave_service

router = APIRouter(prefix="/leaves", tags=["leaves"])


@router.get("", response_model=LeaveListResponse)
async def list_leaves(
    db: DbSession,
    current: CurrentUserDep,
    employee_id: UUID | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> LeaveListResponse:
    current.require_permission("payroll.read")
    if current.org_id is None:
        return LeaveListResponse(items=[], total=0, page=page, page_size=page_size)
    items, total = await leave_service.list_leaves(
        db, current.org_id, employee_id=employee_id, status=status, page=page, page_size=page_size
    )
    return LeaveListResponse(items=[LeaveRequestResponse.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("", response_model=LeaveRequestResponse, status_code=201)
async def create_leave(data: LeaveRequestCreate, db: DbSession, current: CurrentUserDep) -> LeaveRequestResponse:
    current.require_permission("payroll.write")
    if current.org_id is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No organization context")
    leave = await leave_service.create_leave(db, current.org_id, data)
    return LeaveRequestResponse.model_validate(leave)


@router.patch("/{leave_id}/review", response_model=LeaveRequestResponse)
async def review_leave(leave_id: UUID, data: LeaveRequestReview, db: DbSession, current: CurrentUserDep) -> LeaveRequestResponse:
    current.require_permission("payroll.write")
    if current.org_id is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No organization context")
    leave = await leave_service.review_leave(db, current.org_id, leave_id, data)
    return LeaveRequestResponse.model_validate(leave)


@router.get("/balance/{employee_id}")
async def get_leave_balance(employee_id: UUID, db: DbSession, current: CurrentUserDep) -> dict:
    current.require_permission("payroll.read")
    if current.org_id is None:
        return {"used": {}, "quota": {}, "remaining": {}}
    return await leave_service.get_leave_balance(db, current.org_id, employee_id)
