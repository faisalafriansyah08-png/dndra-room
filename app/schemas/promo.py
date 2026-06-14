from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal


class PromoBase(BaseModel):
    title: str
    code: str
    discount_percent: Optional[int] = None
    discount_amount: Optional[Decimal] = None
    min_transaction: Decimal = 0
    max_discount: Optional[Decimal] = None
    start_date: date
    end_date: date
    usage_limit: Optional[int] = None


class PromoCreate(PromoBase):
    pass


class PromoResponse(PromoBase):
    id: int
    usage_count: int
    active: bool
    
    class Config:
        from_attributes = True


class PromoValidate(BaseModel):
    code: str
    total_amount: Decimal


class PromoValidateResponse(BaseModel):
    valid: bool
    discount_amount: Decimal
    final_amount: Decimal
    message: Optional[str] = None

