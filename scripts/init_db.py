"""
Script untuk inisialisasi database dan create tables
Run: python scripts/init_db.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base, engine
from app.models import User, Room, Booking, Payment, Promo, SupportMessage

def init_database():
    """Create all tables in the database"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_database()