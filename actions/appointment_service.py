from utils.backend_client import backend_client
from loguru import logger
from datetime import date

def get_available_slots(store_id: int, target_date: date = None):
    """Fetch available slots for a store from the backend."""
    return backend_client.get_available_slots(store_id)

def book_appointment(store_id: int, customer_name: str, phone_number: str, appointment_date: date, start_time: str):
    """Submit a booking request to the backend."""
    payload = {
        "store": store_id,
        "name": customer_name,
        "phone_number": phone_number,
        "date": appointment_date.isoformat(),
        "start_time": start_time
    }
    return backend_client.book_appointment(payload)
