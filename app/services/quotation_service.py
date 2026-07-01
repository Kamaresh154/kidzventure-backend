import uuid
from datetime import date

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.quotation import Quotation, QuotationLine
from app.schemas.quotation import QuotationCreate, QuotationStatusUpdate


async def list_quotations(
    db: AsyncSession,
    org_id: uuid.UUID,
    *,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Quotation], int]:
    q = (
        select(Quotation)
        .where(Quotation.organization_id == org_id, Quotation.deleted_at.is_(None))
        .options(selectinload(Quotation.lines))
    )
    if status:
        q = q.where(Quotation.status == status)
    total = (await db.execute(select(func.count()).select_from(
        select(Quotation).where(Quotation.organization_id == org_id, Quotation.deleted_at.is_(None)).subquery()
    ))).scalar_one()
    items = (
        await db.execute(q.order_by(Quotation.created_at.desc()).offset((page - 1) * page_size).limit(page_size))
    ).scalars().all()
    return list(items), total


async def create_quotation(db: AsyncSession, org_id: uuid.UUID, data: QuotationCreate) -> Quotation:
    total = await db.execute(
        select(func.count()).select_from(
            select(Quotation).where(Quotation.organization_id == org_id).subquery()
        )
    )
    count = total.scalar_one()
    quote_no = f"Q-{str(count + 1).zfill(4)}"
    subtotal = sum(line.line_total for line in data.lines)
    tax_amount = subtotal * float(data.tax_rate) / 100
    grand_total = subtotal + tax_amount

    quotation = Quotation(
        organization_id=org_id,
        quote_no=quote_no,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        customer_email=data.customer_email,
        subtotal=subtotal,
        tax_rate=data.tax_rate,
        tax_amount=tax_amount,
        total=grand_total,
        notes=data.notes,
        status="draft",
        created_by=data.created_by,
        created_at_date=date.today(),
    )
    for line_data in data.lines:
        quotation.lines.append(QuotationLine(**line_data.model_dump()))
    db.add(quotation)
    await db.commit()
    result = await db.execute(
        select(Quotation).where(Quotation.id == quotation.id).options(selectinload(Quotation.lines))
    )
    return result.scalar_one()


async def update_quotation_status(
    db: AsyncSession, org_id: uuid.UUID, quotation_id: uuid.UUID, data: QuotationStatusUpdate
) -> Quotation:
    quotation = await _get_quotation(db, org_id, quotation_id)
    valid_transitions = {"draft": ["sent"], "sent": ["accepted", "rejected"]}
    if quotation.status in valid_transitions:
        if data.status not in valid_transitions[quotation.status]:
            raise HTTPException(status_code=400, detail=f"Cannot transition from {quotation.status} to {data.status}")
    quotation.status = data.status
    await db.commit()
    result = await db.execute(
        select(Quotation).where(Quotation.id == quotation_id).options(selectinload(Quotation.lines))
    )
    return result.scalar_one()


async def delete_quotation(db: AsyncSession, org_id: uuid.UUID, quotation_id: uuid.UUID) -> None:
    from datetime import datetime, timezone
    quotation = await _get_quotation(db, org_id, quotation_id)
    quotation.deleted_at = datetime.now(timezone.utc)
    await db.commit()


async def _get_quotation(db: AsyncSession, org_id: uuid.UUID, quotation_id: uuid.UUID) -> Quotation:
    result = await db.execute(
        select(Quotation).where(Quotation.id == quotation_id, Quotation.organization_id == org_id, Quotation.deleted_at.is_(None))
    )
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return q
