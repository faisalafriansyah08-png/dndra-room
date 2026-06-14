"""
Script untuk test koneksi database
Run: python scripts/test_connection.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import text
from app.database import engine, SessionLocal
from app.config import get_settings

settings = get_settings()


def test_connection():
    """Test database connection"""
    print("\n🔌 Testing database connection...\n")
    print(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'hidden'}\n")
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print("✅ Database connection successful!")
            print(f"PostgreSQL version: {version}\n")
        
        # Test session
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"✅ Current database: {db_name}")
            
            # Count tables
            result = db.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = result.fetchone()[0]
            print(f"✅ Tables in database: {table_count}\n")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database connection failed!")
        print(f"Error: {e}\n")
        return False
    
    return True


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
