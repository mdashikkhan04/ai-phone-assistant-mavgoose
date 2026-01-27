import json
import os
from pathlib import Path
from fastapi import APIRouter, Request, Response
from twilio.twiml.voice_response import VoiceResponse
from core.state_machine import start_fsm
from actions.sms_service import send_booking_sms
from core.store_resolver import resolve_store
from actions.transfer_service import initiate_warm_transfer
from database.call_logs import log_call_event
from core import prompt_manager

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
BOOKING_LINKS_FILE = BASE_DIR / "data" / "booking_links.json"

@router.post("/gather")
async def handle_gather(request: Request):
    """
    Handles speech transcript, pricing offers, and SMS consent.
    """
    form_data = await request.form()
    transcript = form_data.get("SpeechResult", "").strip()
    from_number = form_data.get("From", "")
    called_number = form_data.get("Called", "")
    call_sid = form_data.get("CallSid", "")

    if not transcript:
        response = VoiceResponse()
        response.say(
            prompt_manager.get_repeat_prompt(),
            voice="alice",
            language="en-US"
        )
        return Response(content=str(response), media_type="application/xml")

    # Consent detection for SMS
    YES_WORDS = ["yes", "yeah", "yep", "sure", "okay", "ok", "please do"]
    transcript_lower = transcript.lower()
    is_consent = any(word in transcript_lower for word in YES_WORDS)

    # Resolve store for context
    store = resolve_store(called_number)
    store_id = store.get("store_id", "default")

    if is_consent:
        # Log consent event
        log_call_event({
            "call_sid": call_sid,
            "store_id": store_id,
            "intent": "sms_consent",
            "response_type": "sms_processing",
            "sms_sent": False
        })

        # Load booking links
        booking_url = None
        if os.path.exists(BOOKING_LINKS_FILE):
            with open(BOOKING_LINKS_FILE, "r") as f:
                links = json.load(f)
                booking_url = links.get(store_id)
        
        if booking_url:
            # Send SMS
            send_booking_sms(from_number, booking_url)

            # Log SMS sent
            log_call_event({
                "call_sid": call_sid,
                "store_id": store_id,
                "intent": "sms_consent",
                "response_type": "sms_sent",
                "sms_sent": True
            })

            response = VoiceResponse()
            response.say(prompt_manager.get_sms_sent_confirmation(), voice="alice", language="en-US")
            return Response(content=str(response), media_type="application/xml")
        else:
            print(f"WARNING: No booking URL found for store_id: {store_id}. SMS NOT SENT.")

    print(f"Captured Transcript: {transcript}")

    # Pass to FSM and get result (include store_id and call_sid)
    fsm_result = start_fsm(transcript, store_id, call_sid)
    response_type = fsm_result.get("response_type")
    payload = fsm_result.get("response_payload", {})
    intent = fsm_result.get("intent")

    response = VoiceResponse()

    if response_type == "price_found":
        price = payload.get("price")
        msg = prompt_manager.get_pricing_found(price)
        response.say(msg, voice="alice", language="en-US")
    
    elif response_type == "warm_transfer":
        msg = prompt_manager.get_transfer_message()
        response.say(msg, voice="alice", language="en-US")
        
        # Execute transfer
        store_phone = payload.get("store_phone_number")
        briefing = payload.get("briefing_text")
        
        print(f"LOG: Initiating transfer to {store_phone}")
        
        # Log transfer attempt
        log_call_event({
            "call_sid": call_sid,
            "store_id": store_id,
            "intent": intent,
            "response_type": "warm_transfer_initiated",
            "transfer_attempted": True
        })

        success = initiate_warm_transfer(call_sid, store_phone, briefing)
        
        if not success:
            print("LOG: Transfer failed. Offering booking link fallback.")
            response.say(prompt_manager.get_transfer_failed(), voice="alice", language="en-US")
            response.gather(input="speech", action="/webhooks/gather", method="POST", speech_timeout="3")
    
    elif response_type == "offer_booking_sms":
        msg = prompt_manager.get_booking_offer()
        response.say(msg, voice="alice", language="en-US")
        # Listen for the "Yes"
        response.gather(input="speech", action="/webhooks/gather", method="POST", speech_timeout="3")
    
    elif response_type == "price_not_found":
        msg = prompt_manager.get_pricing_not_found()
        response.say(msg, voice="alice", language="en-US")
    
    elif response_type == "pricing_restricted":
        msg = prompt_manager.get_pricing_restricted()
        response.say(msg, voice="alice", language="en-US")
    
    else:
        response.say(prompt_manager.get_fallback_message(), voice="alice", language="en-US")
    
    # Keep the call alive
    response.pause(length=1) 
    
    return Response(content=str(response), media_type="application/xml")
