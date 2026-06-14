from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class PaymentGateway(str, enum.Enum):
    XENDIT = "xendit"
    MIDTRANS = "midtrans"
    MANUAL = "manual"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"
    REJECTED = "rejected"


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    gateway = Column(Enum(PaymentGateway), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_ref = Column(String, unique=True, index=True)
    payment_url = Column(Text)
    proof_image = Column(String, nullable=True)      # ← BARU: path bukti transfer
    staff_notes = Column(Text, nullable=True)         # ← BARU: catatan staff
    details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    booking = relationship("Booking", back_populates="payment")