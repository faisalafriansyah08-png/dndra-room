from datetime import date, datetime
from typing import Tuple


def validate_booking_dates(check_in: date, check_out: date) -> Tuple[bool, str]:
    """Validate booking dates"""
    today = datetime.now().date()
    
    if check_in < today:
        return False, "Check-in date cannot be in the past"
    
    if check_out <= check_in:
        return False, "Check-out date must be after check-in date"
    
    if (check_out - check_in).days > 30:
        return False, "Maximum booking duration is 30 days"
    
    return True, "Valid"


def generate_booking_code() -> str:
    """Generate unique booking code"""
    import random
    import string
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"BK{timestamp}{random_str}"