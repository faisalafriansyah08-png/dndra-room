from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class SupportStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class SupportMessage(Base):
    __tablename__ = "support_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(SupportStatus), default=SupportStatus.OPEN)
    response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="support_messages")