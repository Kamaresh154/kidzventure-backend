from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class QuotationLineCreate(BaseModel):
    product_id: str
    product_name: str
    sku: str | None = None
    qty: int = Field(ge=1)
    unit_price: Decimal = Field(ge=0)
    line_total: Decimal = Field(ge=0)


class QuotationCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=255)
    customer_phone: str | None = None
    customer_email: str | None = None
    tax_rate: Decimal = Field(default=Decimal("18"), ge=0)
    notes: str | None = None
    lines: list[QuotationLineCreate] = Field(min_length=1)
    created_by: str = Field(min_length=1)


class QuotationStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(sent|accepted|rejected)$")


class QuotationLineResponse(ORMModel):
    id: UUID
    quotation_id: UUID
    product_id: str
    product_name: str
    sku: str | None
    qty: int
    unit_price: Decimal
    line_total: Decimal


class QuotationResponse(ORMModel):
    id: UUID
    organization_id: UUID
    quote_no: str
    customer_name: str
    customer_phone: str | None
    customer_email: str | None
    subtotal: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total: Decimal
    notes: str | None
    status: str
    created_by: str
    created_at_date: date | None
    lines: list[QuotationLineResponse] = []
    created_at: object
    updated_at: object


class QuotationListResponse(BaseModel):
    items: list[QuotationResponse]
    total: int
    page: int
    page_size: int
