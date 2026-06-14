from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.support import SupportMessage, SupportStatus
from app.models.user import User, UserRole
from app.schemas.support import SupportCreate, SupportResponse, SupportUpdate
from app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/support")


@router.post("/", response_model=SupportResponse, status_code=201)
def create_support_ticket(
    support: SupportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new support ticket"""
    ticket = SupportMessage(
        user_id=current_user.id,
        subject=support.subject,
        message=support.message
    )
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/", response_model=List[SupportResponse])
def get_support_tickets(
    status: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get support tickets"""
    query = db.query(SupportMessage)
    
    # Regular users see only their tickets
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        query = query.filter(SupportMessage.user_id == current_user.id)
    
    # Filter by status
    if status:
        try:
            query = query.filter(SupportMessage.status == SupportStatus(status))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    tickets = query.order_by(SupportMessage.created_at.desc()).offset(skip).limit(limit).all()
    return tickets


@router.get("/{ticket_id}", response_model=SupportResponse)
def get_support_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get support ticket by ID"""
    ticket = db.query(SupportMessage).filter(SupportMessage.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check authorization
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF] and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return ticket


@router.put("/{ticket_id}", response_model=SupportResponse)
def update_support_ticket(
    ticket_id: int,
    ticket_update: SupportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.STAFF]))
):
    """Update support ticket (Admin/Staff only)"""
    ticket = db.query(SupportMessage).filter(SupportMessage.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    update_data = ticket_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status":
            try:
                ticket.status = SupportStatus(value)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid status")
        else:
            setattr(ticket, field, value)
    
    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}")
def delete_support_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Delete support ticket (Admin only)"""
    ticket = db.query(SupportMessage).filter(SupportMessage.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db.delete(ticket)
    db.commit()
    
    return {"message": "Ticket deleted successfully"}