from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import date
from app.database import get_db
from app.models.promo import Promo
from app.models.user import UserRole
from app.schemas.promo import PromoCreate, PromoResponse, PromoValidate, PromoValidateResponse
from app.dependencies import require_role
from decimal import Decimal

router = APIRouter(prefix="/promos")


@router.get("/", response_model=List[PromoResponse])
def get_promos(
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of promos"""
    query = db.query(Promo)
    
    if active_only:
        today = date.today()
        query = query.filter(
            and_(
                Promo.active == True,
                Promo.start_date <= today,
                Promo.end_date >= today
            )
        )
    
    promos = query.offset(skip).limit(limit).all()
    return promos


@router.get("/{promo_id}", response_model=PromoResponse)
def get_promo(promo_id: int, db: Session = Depends(get_db)):
    """Get promo by ID"""
    promo = db.query(Promo).filter(Promo.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promo not found")
    return promo


@router.post("/validate", response_model=PromoValidateResponse)
def validate_promo(
    promo_data: PromoValidate,
    db: Session = Depends(get_db)
):
    """Validate promo code and calculate discount"""
    promo = db.query(Promo).filter(
        and_(
            Promo.code == promo_data.code,
            Promo.active == True,
            Promo.start_date <= date.today(),
            Promo.end_date >= date.today()
        )
    ).first()
    
    if not promo:
        return {
            "valid": False,
            "discount_amount": 0,
            "final_amount": promo_data.total_amount,
            "message": "Invalid or expired promo code"
        }
    
    # Check usage limit
    if promo.usage_limit and promo.usage_count >= promo.usage_limit:
        return {
            "valid": False,
            "discount_amount": 0,
            "final_amount": promo_data.total_amount,
            "message": "Promo code usage limit reached"
        }
    
    # Check minimum transaction
    if promo_data.total_amount < promo.min_transaction:
        return {
            "valid": False,
            "discount_amount": 0,
            "final_amount": promo_data.total_amount,
            "message": f"Minimum transaction is Rp {promo.min_transaction:,.0f}"
        }
    
    # Calculate discount
    discount = Decimal(0)
    if promo.discount_percent:
        discount = promo_data.total_amount * Decimal(promo.discount_percent / 100)
    elif promo.discount_amount:
        discount = promo.discount_amount
    
    # Apply max discount
    if promo.max_discount and discount > promo.max_discount:
        discount = promo.max_discount
    
    final_amount = promo_data.total_amount - discount
    
    return {
        "valid": True,
        "discount_amount": discount,
        "final_amount": final_amount,
        "message": f"Promo applied! You save Rp {discount:,.0f}"
    }


@router.post("/", response_model=PromoResponse, status_code=201)
def create_promo(
    promo: PromoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role([UserRole.ADMIN]))
):
    """Create new promo (Admin only)"""
    # Check if code already exists
    existing = db.query(Promo).filter(Promo.code == promo.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Promo code already exists")
    
    new_promo = Promo(**promo.dict())
    db.add(new_promo)
    db.commit()
    db.refresh(new_promo)
    return new_promo


@router.put("/{promo_id}", response_model=PromoResponse)
def update_promo(
    promo_id: int,
    promo_update: PromoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_role([UserRole.ADMIN]))
):
    """Update promo (Admin only)"""
    promo = db.query(Promo).filter(Promo.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promo not found")
    
    update_data = promo_update.dict()
    for field, value in update_data.items():
        setattr(promo, field, value)
    
    db.commit()
    db.refresh(promo)
    return promo


@router.delete("/{promo_id}")
def delete_promo(
    promo_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_role([UserRole.ADMIN]))
):
    """Delete promo (Admin only)"""
    promo = db.query(Promo).filter(Promo.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promo not found")
    
    # Soft delete - set active to False
    promo.active = False
    db.commit()
    
    return {"message": "Promo deleted successfully"}