from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class PaymentCreate(BaseModel):
    booking_id: int
    gateway: str


class PaymentConfirmAction(BaseModel):
    action: str   # "approve" atau "reject"
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: Decimal
    gateway: str
    status: str
    transaction_ref: Optional[str] = None
    payment_url: Optional[str] = None
    proof_image: Optional[str] = None
    staff_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentWebhook(BaseModel):
    external_id: str
    status: str
    amount: Optional[Decimal] = None
    payment_method: Optional[str] = None