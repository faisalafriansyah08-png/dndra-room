"""
Script untuk mengisi data awal (seed data) ke database
Run: python scripts/seed_data.py
"""
import sys
import os
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.room import Room, RoomStatus
from app.models.promo import Promo
from app.utils.security import get_password_hash


def seed_users(db):
    """Seed user data"""
    print("Seeding users...")
    
    users = [
        User(
            name="Admin Hotel",
            email="admin@hotel.com",
            phone="+6281234567890",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN
        ),
        User(
            name="Staff Resepsionis",
            email="staff@hotel.com",
            phone="+6281234567891",
            password_hash=get_password_hash("staff123"),
            role=UserRole.STAFF
        ),
        User(
            name="John Doe",
            email="john@example.com",
            phone="+6281234567892",
            password_hash=get_password_hash("user123"),
            role=UserRole.USER
        ),
        User(
            name="Jane Smith",
            email="jane@example.com",
            phone="+6281234567893",
            password_hash=get_password_hash("user123"),
            role=UserRole.USER
        )
    ]
    
    for user in users:
        existing = db.query(User).filter(User.email == user.email).first()
        if not existing:
            db.add(user)
    
    db.commit()
    print(f"✅ Seeded {len(users)} users")


def seed_rooms(db):
    """Seed room data"""
    print("Seeding rooms...")
    
    rooms = [
        Room(
            code="STD-101",
            name="Standard Room",
            description="Kamar nyaman dengan fasilitas standar, cocok untuk solo traveler atau pasangan.",
            price=Decimal("350000"),
            capacity=2,
            images=[
                "https://images.unsplash.com/photo-1611892440504-42a792e24d32",
                "https://images.unsplash.com/photo-1631049307264-da0ec9d70304"
            ],
            amenities=["AC", "TV", "WiFi", "Private Bathroom", "Mini Fridge"],
            status=RoomStatus.AVAILABLE
        ),
        Room(
            code="DLX-201",
            name="Deluxe Room",
            description="Kamar lebih luas dengan pemandangan kota, dilengkapi balkon pribadi.",
            price=Decimal("550000"),
            capacity=2,
            images=[
                "https://images.unsplash.com/photo-1590490360182-c33d57733427",
                "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b"
            ],
            amenities=["AC", "Smart TV", "WiFi", "Private Bathroom", "Mini Bar", "Balcony", "Coffee Maker"],
            status=RoomStatus.AVAILABLE
        ),
        Room(
            code="SUI-301",
            name="Suite Room",
            description="Kamar suite mewah dengan ruang tamu terpisah, cocok untuk keluarga atau bisnis.",
            price=Decimal("850000"),
            capacity=4,
            images=[
                "https://images.unsplash.com/photo-1566665797739-1674de7a421a",
                "https://images.unsplash.com/photo-1578683010236-d716f9a3f461"
            ],
            amenities=["AC", "Smart TV", "WiFi", "Private Bathroom", "Living Room", "Kitchenette", "Bathtub", "City View"],
            status=RoomStatus.AVAILABLE
        ),
        Room(
            code="STD-102",
            name="Standard Twin Room",
            description="Kamar dengan 2 tempat tidur single, ideal untuk teman atau keluarga kecil.",
            price=Decimal("400000"),
            capacity=2,
            images=[
                "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6",
                "https://images.unsplash.com/photo-1598928506311-c55ded91a20c"
            ],
            amenities=["AC", "TV", "WiFi", "Private Bathroom", "Work Desk"],
            status=RoomStatus.AVAILABLE
        ),
        Room(
            code="FAM-401",
            name="Family Room",
            description="Kamar keluarga luas dengan kapasitas hingga 5 orang.",
            price=Decimal("950000"),
            capacity=5,
            images=[
                "https://images.unsplash.com/photo-1595576508898-0ad5c879a061",
                "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af"
            ],
            amenities=["AC", "Smart TV", "WiFi", "Private Bathroom", "Extra Beds", "Mini Fridge", "Dining Area"],
            status=RoomStatus.AVAILABLE
        ),
        Room(
            code="DLX-202",
            name="Deluxe Ocean View",
            description="Kamar deluxe dengan pemandangan laut yang menakjubkan.",
            price=Decimal("750000"),
            capacity=2,
            images=[
                "https://images.unsplash.com/photo-1618773928121-c32242e63f39",
                "https://images.unsplash.com/photo-1584132967334-10e028bd69f7"
            ],
            amenities=["AC", "Smart TV", "WiFi", "Private Bathroom", "Ocean View", "Balcony", "Mini Bar"],
            status=RoomStatus.AVAILABLE
        ),
        Room(
            code="STD-103",
            name="Standard Room",
            description="Kamar standar yang sedang dalam maintenance.",
            price=Decimal("350000"),
            capacity=2,
            images=[],
            amenities=["AC", "TV", "WiFi", "Private Bathroom"],
            status=RoomStatus.MAINTENANCE
        )
    ]
    
    for room in rooms:
        existing = db.query(Room).filter(Room.code == room.code).first()
        if not existing:
            db.add(room)
    
    db.commit()
    print(f"✅ Seeded {len(rooms)} rooms")


def seed_promos(db):
    """Seed promo data"""
    print("Seeding promos...")
    
    today = date.today()
    
    promos = [
        Promo(
            title="Diskon Awal Tahun",
            code="NEWYEAR2025",
            discount_percent=20,
            min_transaction=Decimal("500000"),
            max_discount=Decimal("200000"),
            start_date=today,
            end_date=today + timedelta(days=30),
            usage_limit=100,
            usage_count=0,
            active=True
        ),
        Promo(
            title="Weekend Special",
            code="WEEKEND50",
            discount_amount=Decimal("50000"),
            min_transaction=Decimal("300000"),
            start_date=today,
            end_date=today + timedelta(days=60),
            usage_limit=50,
            usage_count=0,
            active=True
        ),
        Promo(
            title="First Booking Discount",
            code="FIRST100",
            discount_amount=Decimal("100000"),
            min_transaction=Decimal("400000"),
            start_date=today,
            end_date=today + timedelta(days=90),
            usage_limit=200,
            usage_count=0,
            active=True
        ),
        Promo(
            title="Member Special 15%",
            code="MEMBER15",
            discount_percent=15,
            min_transaction=Decimal("600000"),
            max_discount=Decimal("150000"),
            start_date=today,
            end_date=today + timedelta(days=45),
            usage_limit=None,  # Unlimited
            usage_count=0,
            active=True
        ),
        Promo(
            title="Flash Sale 30%",
            code="FLASH30",
            discount_percent=30,
            min_transaction=Decimal("700000"),
            max_discount=Decimal("300000"),
            start_date=today,
            end_date=today + timedelta(days=7),
            usage_limit=20,
            usage_count=0,
            active=True
        )
    ]
    
    for promo in promos:
        existing = db.query(Promo).filter(Promo.code == promo.code).first()
        if not existing:
            db.add(promo)
    
    db.commit()
    print(f"✅ Seeded {len(promos)} promos")


def seed_all():
    """Seed all data"""
    db = SessionLocal()
    
    try:
        print("\n🌱 Starting database seeding...\n")
        
        seed_users(db)
        seed_rooms(db)
        seed_promos(db)
        
        print("\n✅ Database seeding completed successfully!\n")
        print("📋 Default credentials:")
        print("   Admin: admin@hotel.com / admin123")
        print("   Staff: staff@hotel.com / staff123")
        print("   User:  john@example.com / user123\n")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
