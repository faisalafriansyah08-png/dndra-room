from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models.room import Room, RoomStatus
from app.models.user import UserRole
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse, RoomAvailability
from app.dependencies import get_current_user, require_role
from app.services.booking_service import BookingService
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
import os, uuid, shutil
router = APIRouter(prefix="/rooms")


@router.get("/", response_model=List[RoomResponse])
def get_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    check_in: Optional[date] = None,
    check_out: Optional[date] = None,
    min_capacity: Optional[int] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get list of rooms with optional filters"""
    query = db.query(Room).filter(Room.status == RoomStatus.AVAILABLE)
    
    if min_capacity:
        query = query.filter(Room.capacity >= min_capacity)
    
    if max_price:
        query = query.filter(Room.price <= max_price)
    
    rooms = query.offset(skip).limit(limit).all()
    
    # If dates provided, filter by availability
    if check_in and check_out:
        available_rooms = []
        for room in rooms:
            if BookingService.check_room_availability(db, room.id, check_in, check_out):
                available_rooms.append(room)
        return available_rooms
    
    return rooms

@router.get("/all", response_model=List[RoomResponse])
def get_all_rooms(
    db: Session = Depends(get_db),
    current_user = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """Get ALL rooms regardless of status — admin/staff only"""
    return db.query(Room).order_by(Room.id).all()

@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    """Get room details by ID"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.post("/check-availability", response_model=RoomAvailability)
def check_availability(
    room_id: int,
    check_in: date,
    check_out: date,
    db: Session = Depends(get_db)
):
    """Check room availability for specific dates"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    available = BookingService.check_room_availability(db, room_id, check_in, check_out)
    
    return {
        "room_id": room_id,
        "check_in": check_in,
        "check_out": check_out,
        "available": available,
        "message": "Room is available" if available else "Room is not available for selected dates"
    }


@router.post("/", response_model=RoomResponse, status_code=201)
def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """Create a new room (Admin/Staff only)"""
    # Check if room code already exists
    existing = db.query(Room).filter(Room.code == room.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Room code already exists")
    
    new_room = Room(**room.dict())
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    room_update: RoomUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """Update room (Admin/Staff only)"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Update fields
    update_data = room_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(room, field, value)
    
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}")
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role([UserRole.ADMIN]))
):
    """Delete room (Admin only)"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Instead of deleting, set status to disabled
    room.status = RoomStatus.DISABLED
    db.commit()
    
    return {"message": "Room disabled successfully"}

@router.post("/{room_id}/upload-image")
async def upload_room_image(
    room_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """Upload gambar untuk kamar (Admin/Staff only)"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Validasi tipe file
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File harus berupa gambar (jpg, png, webp)")

    # Buat nama file unik
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = f"uploads/rooms/{filename}"

    # Simpan file
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update images di database
    current_images = room.images or []
    image_url = f"http://localhost:8000/uploads/rooms/{filename}"
    room.images = current_images + [image_url]
    db.commit()
    db.refresh(room)

    return {"image_url": image_url, "images": room.images}


@router.delete("/{room_id}/delete-image")
def delete_room_image(
    room_id: int,
    image_url: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """Hapus gambar kamar"""
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Hapus dari list
    current_images = room.images or []
    room.images = [img for img in current_images if img != image_url]
    db.commit()

    # Hapus file fisik kalau bukan URL eksternal
    if "/uploads/rooms/" in image_url:
        filename = image_url.split("/uploads/rooms/")[-1]
        filepath = f"uploads/rooms/{filename}"
        if os.path.exists(filepath):
            os.remove(filepath)

    return {"message": "Image deleted", "images": room.images}