from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class OrderLineCreate(BaseModel):
    product_id: str
    product_name: str
    qty: int = Field(ge=1)
    unit_price: Decimal = Field(ge=0)
    total: Decimal = Field(ge=0)


class OrderCreate(BaseModel):
    customer: str = Field(min_length=1, max_length=255)
    phone: str | None = None
    address: str | None = None
    date: date
    notes: str | None = None
    payment_method: str | None = Field(default=None, pattern="^(gpay|cod|cash|pending)?$")
    assigned_to: str | None = None
    lines: list[OrderLineCreate] = Field(min_length=1)


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(confirmed|dispatched|delivered|cancelled)$")
    changed_by: str


class OrderPaymentVerify(BaseModel):
    payment_ref: str = Field(min_length=1)
    payment_method: str = Field(..., pattern="^(gpay|cash|cod)$")


class OrderLineResponse(ORMModel):
    id: UUID
    order_id: UUID
    product_id: str
    product_name: str
    qty: int
    unit_price: Decimal
    total: Decimal


class OrderResponse(ORMModel):
    id: UUID
    organization_id: UUID
    order_no: str
    customer: str
    phone: str | None
    address: str | None
    date: date
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    status: str
    payment_method: str | None
    payment_ref: str | None
    payment_status: str
    upi_ref_submitted: str | None
    notes: str | None
    placed_by: str
    placed_by_role: str
    assigned_to: str | None
    purchase_employee: str | None
    status_history: list
    lines: list[OrderLineResponse] = []
    created_at: object
    updated_at: object


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    page_size: int
