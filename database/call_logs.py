from datetime import datetime
from utils.backend_client import backend_client
from loguru import logger

def log_call_event(data: dict):
    """
    Logs a call event to the Django backend.
    Expected data fields:
    - call_sid
    - store_id (int)
    - intent
    - response_type
    - pricing_found (bool)
    - sms_sent (bool)
    - transfer_attempted (bool)
    """
    # Map AI part fields to Backend part expected fields
    # Backend CallSession model has fields like:
    # call_type, started_at, ended_at, phone_number, store, duration, etc.
    
    # For now, we'll send the raw data and let the backend handler deal with it,
    # or map it specifically here if we know the backend schema.
    
    event = {
        "call_sid": data.get("call_sid"),
        "store": data.get("store_id"),  # Backend expects store ID
        "call_type": data.get("response_type"),
        "intent": data.get("intent"),
        "metadata": {
            "pricing_found": data.get("pricing_found", False),
            "sms_sent": data.get("sms_sent", False),
            "transfer_attempted": data.get("transfer_attempted", False)
        }
    }

    logger.info(f"Logging call event to backend: {event}")
    
    # Post to backend
    result = backend_client.log_call_event(event)
    
    if not result:
        logger.error(f"Failed to log call event for {data.get('call_sid')} to backend.")
    else:
        logger.success(f"Call event logged successfully to backend.")
