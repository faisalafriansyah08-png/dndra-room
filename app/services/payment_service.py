from sqlalchemy.orm import Session
from app.models.payment import Payment, PaymentStatus, PaymentGateway
from app.models.booking import Booking, BookingStatus
from app.config import get_settings
import httpx
import json
import uuid
from typing import Optional

settings = get_settings()


class PaymentService:
    @staticmethod
    async def create_xendit_invoice(booking: Booking) -> dict:
        """Create Xendit invoice for payment"""
        url = "https://api.xendit.co/v2/invoices"
        headers = {
            "Authorization": f"Basic {settings.XENDIT_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "external_id": booking.booking_code,
            "amount": float(booking.total_price),
            "description": f"Hotel Booking - {booking.booking_code}",
            "invoice_duration": 86400,  # 24 jam
            "currency": "IDR",
            "callback_virtual_account_id": settings.XENDIT_CALLBACK_URL,
            "success_redirect_url": f"{settings.FRONTEND_URL}/booking/success?code={booking.booking_code}",
            "failure_redirect_url": f"{settings.FRONTEND_URL}/booking/failed?code={booking.booking_code}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            return response.json()

    # ✅ Diperbaiki agar transaction_ref selalu unik
    @staticmethod
    def create_payment(db: Session, booking_id: int, gateway: str) -> Payment:
        """Create payment record safely (avoid duplicate key error)"""
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError("Booking not found")
        
        # Generate kode unik untuk transaksi
        transaction_ref = f"{booking.booking_code}-{uuid.uuid4().hex[:8]}"
        
        payment = Payment(
            booking_id=booking_id,
            amount=booking.total_price,
            gateway=PaymentGateway(gateway),
            status=PaymentStatus.PENDING,
            transaction_ref=transaction_ref
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    # ✅ Ditambahkan handling error & logging
    @staticmethod
    def handle_payment_webhook(db: Session, transaction_ref: str, status: str) -> Optional[Payment]:
        """Handle payment webhook notification safely"""
        try:
            payment = db.query(Payment).filter(Payment.transaction_ref == transaction_ref).first()
            if not payment:
                print(f"[WEBHOOK] Transaksi {transaction_ref} tidak ditemukan.")
                return None

            # Update status pembayaran
            if status.upper() in ["PAID", "SETTLED", "SUCCESS"]:
                payment.status = PaymentStatus.SUCCESS
                # Update status booking
                booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
                if booking:
                    booking.status = BookingStatus.CONFIRMED
            elif status.upper() in ["FAILED", "EXPIRED"]:
                payment.status = PaymentStatus.FAILED
            else:
                print(f"[WEBHOOK] Status tidak dikenal: {status}")
                return payment

            db.commit()
            db.refresh(payment)
            print(f"[WEBHOOK] Pembayaran {transaction_ref} diperbarui ke status {payment.status}.")
            return payment

        except Exception as e:
            db.rollback()
            print(f"[ERROR] Gagal memproses webhook {transaction_ref}: {e}")
            return None
