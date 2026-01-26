from core.intent_classifier import classify_intent
from business_logic.pricing_engine import get_repair_price

def start_fsm(transcript: str):
    """
    Initial entry point for the Finite State Machine.
    """
    print(f"FSM Started with transcript: {transcript}")
    
    # Classify intent
    classification = classify_intent(transcript)
    intent = classification['intent']
    is_computer = classification['is_computer_repair']
    
    print(f"Detected Intent: {intent}")
    print(f"Is Computer Repair: {is_computer}")
    
    pricing_info = None
    response_type = "unknown"
    response_payload = {}

    if intent == "pricing":
        if is_computer:
            print("LOG: Pricing is RESTRICTED for computer/laptop repairs.")
            response_type = "pricing_restricted"
        else:
            # VERY SIMPLE and SAFE heuristic for model/issue extraction
            model = None
            issue = None
            category = "phone" # default
            
            transcript_lower = transcript.lower()
            
            # Model detection
            if "iphone 13" in transcript_lower:
                model = "iPhone 13"
            elif "iphone 14" in transcript_lower:
                model = "iPhone 14"
            elif "ipad air 4" in transcript_lower:
                model = "iPad Air 4"
                category = "tablet"
            elif "ps5" in transcript_lower:
                model = "PS5"
                category = "console"
            
            # Issue detection
            if "screen" in transcript_lower:
                issue = "screen"
            elif "battery" in transcript_lower:
                issue = "battery"
            elif "hdmi" in transcript_lower:
                issue = "hdmi port"
                category = "console"

            # Call get_repair_price ONLY if all slots are found
            if model and issue:
                pricing_info = get_repair_price(category, model, issue)
                
                if pricing_info:
                    print(f"LOG: Price found: {pricing_info['price']} {pricing_info['currency']} for {model} {issue}")
                    response_type = "price_found"
                    response_payload = {"price": pricing_info['price']}
                else:
                    print(f"LOG: No pricing found in database for {model} {issue}.")
                    response_type = "price_not_found"
            else:
                print(f"LOG: Pricing could not be determined. Missing slots: model={model}, issue={issue}")
                response_type = "price_not_found"

    return {
        "state": "pricing_check" if intent == "pricing" else "initial", 
        "transcript": transcript,
        "intent": intent,
        "is_computer_repair": is_computer,
        "pricing_info": pricing_info,
        "response_type": response_type,
        "response_payload": response_payload
    }

