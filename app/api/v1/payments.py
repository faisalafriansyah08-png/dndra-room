import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentWebhook, PaymentConfirmAction
from app.services.payment_service import PaymentService
from app.dependencies import get_current_user

router = APIRouter(prefix="/payments")

UPLOAD_DIR = "uploads/proofs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == payment_data.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    payment = PaymentService.create_payment(db, payment_data.booking_id, payment_data.gateway)
    if payment_data.gateway == "xendit":
        try:
            invoice = await PaymentService.create_xendit_invoice(booking)
            payment.payment_url = invoice.get("invoice_url")
            payment.transaction_ref = invoice.get("id")
            db.commit()
            db.refresh(payment)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Payment gateway error: {str(e)}")
    return payment


@router.post("/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        transaction_ref = data.get("external_id") or data.get("id")
        status = data.get("status")
        if not transaction_ref or not status:
            raise HTTPException(status_code=400, detail="Invalid webhook data")
        payment = PaymentService.handle_payment_webhook(db, transaction_ref, status)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return {"message": "Webhook processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending", response_model=list[PaymentResponse])
def get_pending_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Daftar pembayaran pending — khusus staff/admin"""
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    payments = db.query(Payment).filter(Payment.status == "pending").all()
    return payments


@router.post("/{payment_id}/upload-proof", response_model=PaymentResponse)
async def upload_proof(
    payment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload bukti transfer oleh tamu"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validasi tipe file
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Only JPG/PNG allowed")

    # Simpan file
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())

    # Update payment
    payment.proof_image = f"/uploads/proofs/{filename}"
    db.commit()
    db.refresh(payment)
    return payment


@router.put("/{payment_id}/confirm", response_model=PaymentResponse)
def confirm_payment(
    payment_id: int,
    body: PaymentConfirmAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Konfirmasi atau tolak pembayaran — khusus staff/admin"""
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if body.action == "approve":
        payment.status = PaymentStatus.SUCCESS
        # Update booking jadi confirmed
        booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
        if booking:
            booking.status = BookingStatus.CONFIRMED
    elif body.action == "reject":
        payment.status = PaymentStatus.REJECTED
    else:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")

    payment.staff_notes = body.notes
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/{booking_id}", response_model=PaymentResponse)
def get_payment_status(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment = db.query(Payment).filter(Payment.booking_id == booking_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return payment