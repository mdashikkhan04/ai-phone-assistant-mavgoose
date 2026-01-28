def get_greeting(store_name: str, store_location: str) -> str:
    """SOP: Engaging & Enthusiastic Greeting."""
    # Note: store_name might already be 'uBreakiFix' or include it. 
    # The requirement says 'Thank you for calling uBreakiFix!'
    return f"Thank you for calling uBreakiFix in {store_location}! This is the AI assistant, what can I fix for you today?"

def get_pricing_found(price: float) -> str:
    """SOP: Pricing builds trust but encourages in-store visits."""
    return (
        f"For that issue, the estimated cost for the repair is typically around {price} dollars. "
        "Our certified technicians use only top-quality parts, and our repairs come with a one-year warranty. "
        "We can usually have that done for you same-day—let’s get you scheduled for a repair so we can get that taken care of quickly!"
    )

def get_pricing_not_found() -> str:
    """SOP: Show genuine empathy and maintain confidence."""
    return (
        "I see this issue all the time—we’ll take great care of you. "
        "I don't have an exact price estimate for that repair right now, but I want to make sure you get the most accurate answer. "
        "Could you please tell me the device model or the specific issue again?"
    )

def get_pricing_restricted() -> str:
    """SOP: Gently position store visit as best next step."""
    return (
        "Actually, computer and laptop repairs require an in-store diagnostic so our certified technicians can be sure of the fix. "
        "Please visit the store or call us during business hours for assistance, and we'll take great care of you."
    )

def get_booking_offer() -> str:
    """SOP: Always secure an appointment, confidence-building."""
    return (
        "We can definitely take care of that for you! Our store is currently closed, "
        "but to ensure a smooth and quick repair, I can send you a link to book an appointment by text right now. "
        "What do you think, should I send that over?"
    )

def get_transfer_justification() -> str:
    """SOP: Frame it as quality control/trust building."""
    return (
        "I want to make sure you get the most accurate answer and the highest quality service. "
        "I’m going to connect you directly with one of our in-store technicians who can help right away."
    )

def get_transfer_context_assurance() -> str:
    return "I’ll let them know exactly what we’ve discussed so you don’t have to repeat yourself."

def get_transfer_instruction() -> str:
    return "This should only take a moment — please stay on the line."

def get_transfer_connecting() -> str:
    return "Alright, I’m connecting you now — thanks for your patience."

def get_transfer_message() -> str:
    return "One moment please, I'm connecting you with one of our experts."

def get_transfer_failed() -> str:
    return "I'm sorry, our team is currently busy and unable to take the call. Would you like me to send you a booking link instead?"

def get_sms_sent_confirmation() -> str:
    return "I've sent the booking link to your phone. Is there anything else I can help with?"

def get_fallback_message() -> str:
    return "Thanks, one moment please while I look into that for you."

def get_repeat_prompt() -> str:
    return "I'm sorry, I didn't catch that. Could you please repeat what you said?"

def get_tech_briefing(device: str, issue: str, reason: str) -> str:
    return (
        f"Hey, this is the AI assistant. I've got a customer on the line. "
        f"They're calling about {device} {issue}. "
        f"I wasn't able to fully confirm {reason}, so I wanted to bring you in. "
        f"They're on the line now - I'll go ahead and connect you."
    )
