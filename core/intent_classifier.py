import re

def classify_intent(transcript: str) -> dict:
    """
    Classifies the caller's intent and checks for computer repair requests using rule-based logic.
    """
    transcript_lower = transcript.lower()

    # Rule-based intent detection
    intent = "unknown"
    
    pricing_keywords = ["price", "cost", "how much", "screen", "battery", "repair"]
    booking_keywords = ["appointment", "book", "schedule", "come in", "visit"]
    transfer_keywords = ["talk to", "representative", "manager", "technician", "person", "human"]
    
    # Check for pricing
    if any(word in transcript_lower for word in pricing_keywords):
        intent = "pricing"
    
    # Check for booking (can override pricing if specific booking words are used)
    if any(word in transcript_lower for word in booking_keywords):
        intent = "booking"

    # Check for transfer
    if any(word in transcript_lower for word in transfer_keywords):
        intent = "transfer"

    # Restriction detection (computer repairs)
    computer_keywords = ["computer", "laptop", "macbook", "pc", "desktop", "surface pro"]
    is_computer_repair = any(word in transcript_lower for word in computer_keywords)

    return {
        "intent": intent,
        "is_computer_repair": is_computer_repair,
        "original_transcript": transcript
    }
