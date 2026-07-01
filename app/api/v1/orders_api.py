from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.core.deps import CurrentUserDep, DbSession
from app.schemas.order import (
    OrderCreate, OrderListResponse, OrderPaymentVerify, OrderResponse, OrderStatusUpdate,
)
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


def _require_org(current: CurrentUserDep) -> UUID:
    if current.org_id is None:
        raise HTTPException(status_code=400, detail="No organization context")
    return current.org_id


@router.get("", response_model=OrderListResponse)
async def list_orders(
    db: DbSession,
    current: CurrentUserDep,
    status: str | None = None,
    payment_status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> OrderListResponse:
    current.require_permission("invoices.read")
    resolved = _require_org(current)
    items, total = await order_service.list_orders(
        db, resolved, status=status, payment_status=payment_status, page=page, page_size=page_size
    )
    return OrderListResponse(items=[OrderResponse.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(data: OrderCreate, db: DbSession, current: CurrentUserDep) -> OrderResponse:
    current.require_permission("invoices.write")
    resolved = _require_org(current)
    roles = current.roles
    role_label = "Super Admin" if "super_admin" in roles else "Admin" if "admin" in roles else "Employee" if "employee" in roles else "Franchise"
    order = await order_service.create_order(db, resolved, data, current.user.full_name, role_label)
    return OrderResponse.model_validate(order)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: UUID, data: OrderStatusUpdate, db: DbSession, current: CurrentUserDep) -> OrderResponse:
    current.require_permission("invoices.write")
    resolved = _require_org(current)
    order = await order_service.update_order_status(db, resolved, order_id, data)
    return OrderResponse.model_validate(order)


@router.post("/{order_id}/submit-upi-ref", response_model=OrderResponse)
async def submit_upi_ref(order_id: UUID, upi_ref: str, db: DbSession, current: CurrentUserDep) -> OrderResponse:
    current.require_permission("invoices.write")
    resolved = _require_org(current)
    order = await order_service.submit_upi_ref(db, resolved, order_id, upi_ref)
    return OrderResponse.model_validate(order)


@router.post("/{order_id}/verify-payment", response_model=OrderResponse)
async def verify_payment(order_id: UUID, data: OrderPaymentVerify, db: DbSession, current: CurrentUserDep) -> OrderResponse:
    current.require_permission("invoices.write")
    resolved = _require_org(current)
    order = await order_service.verify_payment(db, resolved, order_id, data)
    return OrderResponse.model_validate(order)


@router.post("/{order_id}/reject-payment", response_model=OrderResponse)
async def reject_payment(order_id: UUID, db: DbSession, current: CurrentUserDep) -> OrderResponse:
    current.require_permission("invoices.write")
    resolved = _require_org(current)
    order = await order_service.reject_payment(db, resolved, order_id)
    return OrderResponse.model_validate(order)


@router.post("/{order_id}/assign-purchase", response_model=OrderResponse)
async def assign_purchase(order_id: UUID, employee_name: str, db: DbSession, current: CurrentUserDep) -> OrderResponse:
    current.require_permission("invoices.write")
    resolved = _require_org(current)
    order = await order_service.assign_purchase_employee(db, resolved, order_id, employee_name)
    return OrderResponse.model_validate(order)
