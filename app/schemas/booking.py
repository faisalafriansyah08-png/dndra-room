from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


# Nested schemas untuk relasi
class UserNested(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class RoomNested(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        from_attributes = True


class BookingBase(BaseModel):
    room_id: int
    check_in: date
    check_out: date
    guests: int
    notes: Optional[str] = None


class BookingCreate(BookingBase):
    promo_code: Optional[str] = None
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None


class BookingUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class BookingResponse(BookingBase):
    id: int
    booking_code: str
    user_id: int
    total_price: Decimal
    discount_amount: Decimal
    status: str
    promo_code: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[UserNested] = None   # ← BARU
    room: Optional[RoomNested] = None   # ← BARU

    class Config:
        from_attributes = True