from typing import Dict, Any
from utils.twilio_utils import get_twilio_client, get_twilio_credentials
from loguru import logger

def send_booking_sms(to_number: str, booking_url: str, store: Dict[str, Any]):
    """
    Sends a booking link to the customer via store-specific Twilio SMS.
    """
    client = get_twilio_client(store)
    creds = get_twilio_credentials(store)
    from_number = creds.get("from_number")

    if not client or not from_number:
        logger.error(f"Cannot send SMS: Twilio credentials missing for {store.get('name')}")
        return

    message_body = f"You can book your appointment here: {booking_url}"

    try:
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        logger.success(f"SMS Sent successfully for {store.get('name')}: {message.sid}")
    except Exception as e:
        logger.error(f"Failed to send SMS for {store.get('name')}: {e}")
