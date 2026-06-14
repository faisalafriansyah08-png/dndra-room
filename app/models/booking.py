from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_code = Column(String(30), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    guests = Column(Integer, nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)
    promo_code = Column(String(50))
    discount_amount = Column(Numeric(12, 2), default=0)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)