def get_greeting(store_name: str, store_location: str) -> str:
    return f"Hello! Thank you for calling {store_name} in {store_location}. How can I help you today?"

def get_pricing_found(price: float) -> str:
    return f"The estimated cost for that repair is {price} dollars. Would you like help with anything else?"

def get_pricing_not_found() -> str:
    return "I don't have an exact price for that repair right now. Could you please tell me the device model or the specific issue again?"

def get_pricing_restricted() -> str:
    return "Actually, computer and laptop repairs require an in-store diagnostic. Please visit the store or call us during business hours for more assistance."

def get_booking_offer() -> str:
    return "Our store is currently closed. Would you like me to send you a link to book an appointment by text?"

def get_transfer_message() -> str:
    return "One moment please, I'm connecting you with a technician for further assistance."

def get_transfer_failed() -> str:
    return "I'm sorry, our team is currently busy and unable to take the call. Would you like me to send you a booking link instead?"

def get_sms_sent_confirmation() -> str:
    return "I've sent the booking link to your phone. Is there anything else I can help with?"

def get_fallback_message() -> str:
    return "Thanks, one moment please while I look into that for you."

def get_repeat_prompt() -> str:
    return "I'm sorry, I didn't catch that. Could you please repeat what you said?"
