from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.booking import Booking, BookingStatus
from app.models.room import Room, RoomStatus
from app.models.promo import Promo
from app.schemas.booking import BookingCreate
from app.utils.validators import generate_booking_code, validate_booking_dates
from datetime import date
from typing import Optional, List
from decimal import Decimal


class BookingService:
    @staticmethod
    def check_room_availability(db: Session, room_id: int, check_in: date, check_out: date) -> bool:
        """Check if room is available for given dates"""
        # Check if room exists and is available
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room or room.status != RoomStatus.AVAILABLE:
            return False
        
        # Check for conflicting bookings
        conflicting = db.query(Booking).filter(
            and_(
                Booking.room_id == room_id,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN]),
                Booking.check_in < check_out,
                Booking.check_out > check_in
            )
        ).first()
        
        return conflicting is None
    
    @staticmethod
    def calculate_booking_price(db: Session, room_id: int, check_in: date, check_out: date, promo_code: Optional[str] = None) -> dict:
        """Calculate total booking price with promo"""
        room = db.query(Room).filter(Room.id == room_id).first()
        if not room:
            return {"error": "Room not found"}
        
        nights = (check_out - check_in).days
        base_price = room.price * nights
        discount = Decimal(0)
        
        if promo_code:
            promo = db.query(Promo).filter(
                and_(
                    Promo.code == promo_code,
                    Promo.active == True,
                    Promo.start_date <= date.today(),
                    Promo.end_date >= date.today()
                )
            ).first()
            
            if promo:
                if promo.usage_limit and promo.usage_count >= promo.usage_limit:
                    pass  # Promo limit exceeded
                elif base_price < promo.min_transaction:
                    pass  # Minimum transaction not met
                else:
                    if promo.discount_percent:
                        discount = base_price * Decimal(promo.discount_percent / 100)
                    elif promo.discount_amount:
                        discount = promo.discount_amount
                    
                    if promo.max_discount and discount > promo.max_discount:
                        discount = promo.max_discount
        
        total_price = base_price - discount
        
        return {
            "base_price": float(base_price),
            "discount": float(discount),
            "total_price": float(total_price),
            "nights": nights
        }
    
    @staticmethod
    def create_booking(db: Session, user_id: int, booking_data: BookingCreate) -> Booking:
        """Create a new booking"""
        # Validate dates
        valid, message = validate_booking_dates(booking_data.check_in, booking_data.check_out)
        if not valid:
            raise ValueError(message)
        
        # Check availability
        if not BookingService.check_room_availability(db, booking_data.room_id, booking_data.check_in, booking_data.check_out):
            raise ValueError("Room not available for selected dates")
        
        # Calculate price
        price_info = BookingService.calculate_booking_price(
            db, booking_data.room_id, booking_data.check_in, booking_data.check_out, booking_data.promo_code
        )
        
        # Create booking
        booking = Booking(
            booking_code=generate_booking_code(),
            user_id=user_id,
            room_id=booking_data.room_id,
            check_in=booking_data.check_in,
            check_out=booking_data.check_out,
            guests=booking_data.guests,
            total_price=Decimal(str(price_info["total_price"])),
            discount_amount=Decimal(str(price_info["discount"])),
            promo_code=booking_data.promo_code,
            notes=booking_data.notes,
            status=BookingStatus.PENDING
        )
        
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        # Update promo usage if applicable
        if booking_data.promo_code:
            promo = db.query(Promo).filter(Promo.code == booking_data.promo_code).first()
            if promo:
                promo.usage_count += 1
                db.commit()
        
        return booking
    
    @staticmethod
    def get_user_bookings(db: Session, user_id: int) -> List[Booking]:
        """Get all bookings for a user"""
        return db.query(Booking).filter(Booking.user_id == user_id).order_by(Booking.created_at.desc()).all()
