from datetime import datetime, timezone, timedelta

def is_business_hours() -> bool:
    """
    Checks if the current time is within business hours (10 AM - 7 PM EST).
    """
    # EST is UTC-5
    est_tz = timezone(timedelta(hours=-5))
    current_time = datetime.now(est_tz)
    
    # 10:00 to 19:00
    is_after_10 = current_time.hour >= 10
    is_before_7 = current_time.hour < 19
    
    return is_after_10 and is_before_7
