import uuid
from datetime import date, datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderLine
from app.schemas.order import OrderCreate, OrderPaymentVerify, OrderStatusUpdate


async def list_orders(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    status: str | None = None,
    payment_status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Order], int]:
    q = (
        select(Order)
        .where(Order.organization_id == org_id, Order.deleted_at.is_(None))
        .options(selectinload(Order.lines))
    )
    if status:
        q = q.where(Order.status == status)
    if payment_status:
        q = q.where(Order.payment_status == payment_status)
    total = (await db.execute(select(func.count()).select_from(
        select(Order).where(Order.organization_id == org_id, Order.deleted_at.is_(None)).subquery()
    ))).scalar_one()
    items = (
        await db.execute(q.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size))
    ).scalars().all()
    return list(items), total


async def create_order(db: AsyncSession, org_id: uuid.UUID, data: OrderCreate, placed_by: str, placed_by_role: str) -> Order:
    total = await db.execute(
        select(func.count()).select_from(
            select(Order).where(Order.organization_id == org_id).subquery()
        )
    )
    count = total.scalar_one()
    order_no = f"ORD-{str(count + 1).zfill(4)}"
    subtotal = sum(line.total for line in data.lines)
    order = Order(
        organization_id=org_id,
        order_no=order_no,
        customer=data.customer,
        phone=data.phone,
        address=data.address,
        date=data.date,
        subtotal=subtotal,
        discount=0,
        total=subtotal,
        status="pending",
        payment_method=data.payment_method,
        payment_status="unpaid",
        notes=data.notes,
        placed_by=placed_by,
        placed_by_role=placed_by_role,
        assigned_to=data.assigned_to,
        status_history=[{"status": "pending", "changed_by": placed_by, "changed_at": datetime.now(timezone.utc).isoformat()}],
    )
    for line_data in data.lines:
        order.lines.append(OrderLine(**line_data.model_dump()))
    db.add(order)
    await db.commit()
    result = await db.execute(
        select(Order).where(Order.id == order.id).options(selectinload(Order.lines))
    )
    return result.scalar_one()


async def update_order_status(db: AsyncSession, org_id: uuid.UUID, order_id: uuid.UUID, data: OrderStatusUpdate) -> Order:
    order = await _get_order(db, org_id, order_id)
    order.status = data.status
    history = order.status_history or []
    history.append({"status": data.status, "changed_by": data.changed_by, "changed_at": datetime.now(timezone.utc).isoformat()})
    order.status_history = history
    await db.commit()
    result = await db.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.lines))
    )
    return result.scalar_one()


async def submit_upi_ref(db: AsyncSession, org_id: uuid.UUID, order_id: uuid.UUID, upi_ref: str) -> Order:
    order = await _get_order(db, org_id, order_id)
    order.upi_ref_submitted = upi_ref
    order.payment_status = "pending_verification"
    await db.commit()
    result = await db.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.lines))
    )
    return result.scalar_one()


async def verify_payment(db: AsyncSession, org_id: uuid.UUID, order_id: uuid.UUID, data: OrderPaymentVerify) -> Order:
    order = await _get_order(db, org_id, order_id)
    order.payment_ref = data.payment_ref
    order.payment_method = data.payment_method
    order.payment_status = "paid"
    history = order.status_history or []
    history.append({"status": "payment_verified", "changed_by": "admin", "changed_at": datetime.now(timezone.utc).isoformat()})
    order.status_history = history
    await db.commit()
    result = await db.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.lines))
    )
    return result.scalar_one()


async def reject_payment(db: AsyncSession, org_id: uuid.UUID, order_id: uuid.UUID) -> Order:
    order = await _get_order(db, org_id, order_id)
    order.upi_ref_submitted = None
    order.payment_status = "unpaid"
    await db.commit()
    result = await db.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.lines))
    )
    return result.scalar_one()


async def assign_purchase_employee(db: AsyncSession, org_id: uuid.UUID, order_id: uuid.UUID, employee_name: str) -> Order:
    order = await _get_order(db, org_id, order_id)
    order.purchase_employee = employee_name
    await db.commit()
    result = await db.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.lines))
    )
    return result.scalar_one()


async def _get_order(db: AsyncSession, org_id: uuid.UUID, order_id: uuid.UUID) -> Order:
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.organization_id == org_id, Order.deleted_at.is_(None))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
