from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash, verify_password
from typing import Optional


class AuthService:
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            name=user.name,
            phone=user.phone,
            password_hash=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
