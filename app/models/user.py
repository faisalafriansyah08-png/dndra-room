from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    USER = "user"
    STAFF = "staff"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    password_hash = Column(String, nullable=False)
    role = Column (Enum(UserRole, native_enum=False), default=UserRole.USER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    bookings = relationship("Booking", back_populates="user")
    support_messages = relationship("SupportMessage", back_populates="user")