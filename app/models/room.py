from sqlalchemy import Column, Integer, String, Text, Numeric, ARRAY, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class RoomStatus(str, enum.Enum):
    AVAILABLE = "available"
    MAINTENANCE = "maintenance"
    DISABLED = "disabled"


class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(12, 2), nullable=False)
    capacity = Column(Integer, nullable=False)
    images = Column(ARRAY(String), default=[])
    amenities = Column(ARRAY(String), default=[])
    status = Column(Enum(RoomStatus), default=RoomStatus.AVAILABLE)
    
    # Relationships
    bookings = relationship("Booking", back_populates="room")