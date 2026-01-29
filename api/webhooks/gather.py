import json
import os
from pathlib import Path
from fastapi import APIRouter, Request, Response
from twilio.twiml.voice_response import VoiceResponse
from core.state_machine import start_fsm
from actions.sms_service import send_booking_sms
from core.store_resolver import resolve_store_by_did
from actions.transfer_service import initiate_warm_transfer
from database.call_logs import log_call_event
from core import prompt_manager
from loguru import logger

router = APIRouter()

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
    store = resolve_store_by_did(called_number)
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

        # Load booking link from store object
        booking_url = store.get("booking_link")
        
        if booking_url:
            # Send SMS with store context
            send_booking_sms(from_number, booking_url, store)

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
            logger.warning(f"No booking URL found for store: {store.get('name')}. SMS NOT SENT.")

    logger.info(f"Captured Transcript: {transcript}")

    # Pass to FSM and get result (include full store object and call_sid)
    fsm_result = start_fsm(transcript, store, call_sid)
    response_type = fsm_result.get("response_type")
    payload = fsm_result.get("response_payload", {})
    intent = fsm_result.get("intent")
    
    # Store object from FSM result
    current_store = fsm_result.get("store", store)

    response = VoiceResponse()

    if response_type == "price_found":
        price = payload.get("price")
        msg = prompt_manager.get_pricing_found(price)
        response.say(msg, voice="alice", language="en-US")
    
    elif response_type == "warm_transfer":
        # Multi-part Customer-Facing Script (Part 1 & 3) using prompt_manager
        # 1. Reassurance & Justification
        response.say(prompt_manager.get_transfer_justification(), voice="alice", language="en-US")
        response.pause(length=1)
        
        # 2. Assurance (Passing context)
        response.say(prompt_manager.get_transfer_context_assurance(), voice="alice", language="en-US")
        
        # 3. Instruction to stay on the line
        response.say(prompt_manager.get_transfer_instruction(), voice="alice", language="en-US")
        
        # Execute transfer
        store_phone = payload.get("store_phone_number")
        briefing = payload.get("briefing_text")
        
        logger.info(f"Initiating transfer to {store_phone} for store {current_store.get('name')}")
        
        # Log transfer attempt
        log_call_event({
            "call_sid": call_sid,
            "store_id": store_id,
            "intent": intent,
            "response_type": "warm_transfer_initiated",
            "transfer_attempted": True
        })

        # Smoothing message right before execution
        response.say(prompt_manager.get_transfer_connecting(), voice="alice", language="en-US")

        success = initiate_warm_transfer(call_sid, store_phone, briefing, current_store)
        
        if not success:
            logger.warning(f"Transfer failed for {current_store.get('name')}. Offering booking link fallback.")
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
