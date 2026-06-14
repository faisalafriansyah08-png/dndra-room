from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.user import UserRole, User
from app.schemas.booking import BookingCreate, BookingResponse, BookingUpdate
from app.services.booking_service import BookingService
from app.services.email_service import EmailService
from app.dependencies import get_current_user, require_role
from datetime import date
from sqlalchemy import func as sqlfunc
from typing import List, Optional
router = APIRouter(prefix="/bookings")

@router.get("/", response_model=List[BookingResponse])
def get_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's bookings or all bookings (for admin/staff)"""
    if current_user.role in [UserRole.ADMIN, UserRole.STAFF]:
        # Admin/Staff can see all bookings
        bookings = (
            db.query(Booking)
            .options(joinedload(Booking.user), joinedload(Booking.room))  # ← BARU
            .order_by(Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        bookings = (
            db.query(Booking)
            .options(joinedload(Booking.user), joinedload(Booking.room))  # ← BARU
            .filter(Booking.user_id == current_user.id)
            .order_by(Booking.created_at.desc())
            .all()
        )
    return bookings

@router.get("/report/summary", dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))])
def get_booking_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Laporan reservasi untuk admin"""
    from app.models.room import Room
    from app.models.payment import Payment, PaymentStatus

    query = db.query(Booking)

    if start_date:
        query = query.filter(Booking.created_at >= start_date)
    if end_date:
        query = query.filter(Booking.created_at <= end_date)
    if status:
        query = query.filter(Booking.status == status)

    bookings = query.order_by(Booking.created_at.desc()).all()

    # Hitung summary
    total_revenue = sum(
        float(b.total_price) for b in bookings
        if b.status in [BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN, BookingStatus.COMPLETED]
    )

    status_counts = {}
    for b in bookings:
        status_counts[b.status.value] = status_counts.get(b.status.value, 0) + 1

    return {
        "summary": {
            "total_bookings": len(bookings),
            "total_revenue": total_revenue,
            "status_counts": status_counts,
        },
        "bookings": [
            {
                "id": b.id,
                "booking_code": b.booking_code,
                "guest_name": b.user.name if b.user else "-",
                "guest_email": b.user.email if b.user else "-",
                "room_name": b.room.name if b.room else "-",
                "room_code": b.room.code if b.room else "-",
                "check_in": str(b.check_in),
                "check_out": str(b.check_out),
                "guests": b.guests,
                "total_price": float(b.total_price),
                "discount_amount": float(b.discount_amount or 0),
                "promo_code": b.promo_code,
                "status": b.status.value,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in bookings
        ]
    }

@router.post("/", response_model=BookingResponse, status_code=201)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new booking"""
    try:
        booking = BookingService.create_booking(db, current_user.id, booking_data)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{booking_identifier}", response_model=BookingResponse)
def get_booking(
    booking_identifier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Booking).options(
        joinedload(Booking.user), joinedload(Booking.room)
    )
    if booking_identifier.isdigit():
        booking = query.filter(Booking.id == int(booking_identifier)).first()
    else:
        booking = query.filter(Booking.booking_code == booking_identifier).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF] and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """Update booking status (Admin/Staff only)"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Update fields
    update_data = booking_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status":
            # Validate status transition
            try:
                booking.status = BookingStatus(value)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid status")
        else:
            setattr(booking, field, value)
    
    db.commit()
    db.refresh(booking)
    
    # Send email if status changed to confirmed
    if booking.status == BookingStatus.CONFIRMED:
        try:
            EmailService.send_booking_confirmation(booking, booking.user.email)
        except Exception as e:
            print(f"Failed to send email: {e}")
    
    return booking


@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel a booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check authorization
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF] and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Can only cancel pending or confirmed bookings
    if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
        raise HTTPException(status_code=400, detail="Cannot cancel this booking")
    
    booking.status = BookingStatus.CANCELLED
    db.commit()
    
    return {"message": "Booking cancelled successfully"}