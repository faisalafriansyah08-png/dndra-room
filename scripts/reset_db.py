"""
Script untuk reset database (DROP ALL TABLES + CREATE + SEED)
⚠️ WARNING: This will delete all data!
Run: python scripts/reset_db.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base, engine
from scripts.seed_data import seed_all


def reset_database():
    """Reset database - DROP and CREATE all tables"""
    print("\n⚠️  WARNING: This will delete ALL data in the database!")
    confirm = input("Type 'yes' to confirm: ")
    
    if confirm.lower() != 'yes':
        print("❌ Operation cancelled")
        return
    
    print("\n🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ All tables dropped")
    
    print("\n📦 Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created")
    
    print("\n🌱 Seeding initial data...")
    seed_all()
    
    print("\n✅ Database reset completed!\n")


if __name__ == "__main__":
    reset_database()
