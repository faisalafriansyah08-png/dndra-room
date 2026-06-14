import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings
from app.models.booking import Booking

settings = get_settings()


class EmailService:
    @staticmethod
    def send_booking_confirmation(booking: Booking, user_email: str):
        """Send booking confirmation email"""
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            print("Email service not configured")
            return
        
        subject = f"Booking Confirmation - {booking.booking_code}"
        body = f"""
        Dear {booking.user.name},
        
        Your booking has been confirmed!
        
        Booking Details:
        - Booking Code: {booking.booking_code}
        - Room: {booking.room.name}
        - Check-in: {booking.check_in}
        - Check-out: {booking.check_out}
        - Total Price: Rp {booking.total_price:,.0f}
        
        Thank you for choosing our hotel!
        
        Best regards,
        {settings.APP_NAME}
        """
        
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = user_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            print(f"Email sent to {user_email}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")