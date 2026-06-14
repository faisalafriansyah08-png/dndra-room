from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User, UserRole
from app.dependencies import get_current_user, require_role
from pydantic import BaseModel

router = APIRouter(prefix="/users")


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None


@router.get("/", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    return db.query(User).order_by(User.id).all()


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if body.name: user.name = body.name
    if body.phone: user.phone = body.phone
    if body.role:
        try:
            user.role = UserRole(body.role)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid role")
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}