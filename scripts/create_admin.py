"""
Script untuk membuat user admin baru
Run: python scripts/create_admin.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import get_password_hash


def create_admin():
    """Create admin user interactively"""
    db = SessionLocal()
    
    try:
        print("\n🔑 Create Admin User\n")
        
        name = input("Enter admin name: ")
        email = input("Enter admin email: ")
        phone = input("Enter phone number: ")
        password = input("Enter password: ")
        confirm_password = input("Confirm password: ")
        
        if password != confirm_password:
            print("❌ Passwords don't match!")
            return
        
        # Check if email exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"❌ User with email {email} already exists!")
            return
        
        # Create admin user
        admin = User(
            name=name,
            email=email,
            phone=phone,
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN
        )
        
        db.add(admin)
        db.commit()
        
        print(f"\n✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Role: ADMIN\n")
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()