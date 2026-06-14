from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SupportBase(BaseModel):
    subject: str
    message: str


class SupportCreate(SupportBase):
    pass


class SupportUpdate(BaseModel):
    status: Optional[str] = None
    response: Optional[str] = None


class SupportResponse(SupportBase):
    id: int
    user_id: int
    status: str
    response: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True