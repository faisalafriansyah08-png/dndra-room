from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import date


class RoomBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    price: Decimal
    capacity: int
    images: List[str] = []
    amenities: List[str] = []


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    capacity: Optional[int] = None
    images: Optional[List[str]] = None
    amenities: Optional[List[str]] = None
    status: Optional[str] = None


class RoomResponse(RoomBase):
    id: int
    status: str
    
    class Config:
        from_attributes = True


class RoomAvailability(BaseModel):
    room_id: int
    check_in: date
    check_out: date
    available: bool
    message: Optional[str] = None