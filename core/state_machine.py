import json
import os
from core.intent_classifier import classify_intent
from business_logic.pricing_engine import get_repair_price
from utils.time_utils import is_business_hours
from core.store_resolver import DEFAULT_STORE
from database.call_logs import log_call_event
from core import prompt_manager


def start_fsm(transcript: str, store: dict, call_sid: str = "unknown"):
    """
    Initial entry point for the Finite State Machine.
    """
    store_id = store.get("id")  # Backend integer ID
    print(f"FSM Started for {store.get('name')} with transcript: {transcript}")
    
    # Classify intent
    classification = classify_intent(transcript)
    intent = classification['intent']
    is_computer = classification['is_computer_repair']
    
    transcript_lower = transcript.lower()
    print(f"Detected Intent: {intent}")
    print(f"Is Computer Repair: {is_computer}")
    
    # Complex issue detection
    complex_keywords = ["water damage", "motherboard", "data recovery"]
    is_complex = any(word in transcript_lower for word in complex_keywords)
    
    pricing_info = None
    response_type = "unknown"
    response_payload = {}
    
    # Check business hours
    # Note: Simplified business hours check. Could be expanded to use backend config.
    open_now = is_business_hours()

    # Model and Issue slots for briefing/pricing
    model = None
    issue = None
    category = "phone" # default
    
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

    # LOGIC BRANCHES
    if is_computer:
        print("LOG: Pricing is RESTRICTED for computer/laptop repairs.")
        response_type = "pricing_restricted"
    
    # Case: Warm Transfer (Triggered by intent, complexity, or missing price during business hours)
    elif open_now and (intent == "transfer" or is_complex):
        response_type = "warm_transfer"
    
    elif intent == "pricing":
        if not open_now:
            print("LOG: After-hours pricing intent detected. Offering SMS booking.")
            response_type = "offer_booking_sms"
        else:
            # Attempt to find a price
            if model and issue:
                # Updated signature: (store_id, category, model, issue)
                pricing_info = get_repair_price(store_id, category, model, issue)
                
            if pricing_info:
                print(f"LOG: Price found: {pricing_info['price']} {pricing_info['currency']} for {model} {issue}")
                response_type = "price_found"
                response_payload = {"price": pricing_info['price']}
            else:
                # Pricing not found during business hours -> Warm Transfer
                print(f"LOG: Pricing not determined during business hours. Triggering transfer.")
                response_type = "warm_transfer"
    
    # If Warm Transfer was determined, build the payload
    if response_type == "warm_transfer" and open_now:
        # Backend Store uses 'transfer_number' or 'did'
        transfer_number = store.get("transfer_number") or store.get("did")
        
        # Build structured fields for tech briefing
        device_desc = model if model else "their device"
        issue_desc = issue if issue else "a repair issue"
        
        # Determine transfer reason context exactly as requested
        if intent == "transfer":
            transfer_reason = "their specific request to speak with someone"
        elif is_complex:
            transfer_reason = "the complexity of the repair"
        else:
            transfer_reason = "the exact pricing and turnaround details"
            
        # Format briefing text using prompt_manager
        briefing = prompt_manager.get_tech_briefing(device_desc, issue_desc, transfer_reason)
        
        response_payload = {
            "store_phone_number": transfer_number,
            "briefing_text": briefing,
            "device": device_desc,
            "issue": issue_desc,
            "transfer_reason": transfer_reason
        }

    # Log initial FSM event
    log_call_event({
        "call_sid": call_sid,
        "store_id": store_id,
        "intent": intent,
        "response_type": response_type,
        "pricing_found": pricing_info is not None,
        "sms_sent": False, # Will be logged in webhook if triggered
        "transfer_attempted": False # Will be logged in webhook if triggered
    })

    return {
        "state": "pricing_check" if intent == "pricing" else "initial", 
        "transcript": transcript,
        "intent": intent,
        "is_computer_repair": is_computer,
        "pricing_info": pricing_info,
        "response_type": response_type,
        "response_payload": response_payload,
        "store": store
    }
