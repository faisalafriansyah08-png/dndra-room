from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import List
from app.database import get_db
from app.models.user import User, UserRole
from app.config import get_settings

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/{settings.API_VERSION}/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    return current_user


def require_role(required_roles: List[UserRole]):
    """Dependency to check user role"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Pastikan role yang disimpan di DB sesuai tipe UserRole
        user_role = current_user.role
        if isinstance(user_role, str):
            try:
                user_role = UserRole(user_role)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid user role"
                )

        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user

    return role_checker


