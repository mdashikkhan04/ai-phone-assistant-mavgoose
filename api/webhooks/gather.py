from fastapi import APIRouter, Request, Response
from twilio.twiml.voice_response import VoiceResponse
from core.state_machine import start_fsm

router = APIRouter()

@router.post("/gather")
async def handle_gather(request: Request):
    """
    Handles the speech transcript from Twilio Gather and generates voice responses.
    """
    form_data = await request.form()
    transcript = form_data.get("SpeechResult", "").strip()

    if not transcript:
        response = VoiceResponse()
        response.say(
            "Sorry, I didn’t catch that. Could you please repeat?",
            voice="alice",
            language="en-US"
        )
        return Response(content=str(response), media_type="application/xml")

    print(f"Captured Transcript: {transcript}")

    # Pass to FSM and get result
    fsm_result = start_fsm(transcript)
    response_type = fsm_result.get("response_type")
    payload = fsm_result.get("response_payload", {})

    response = VoiceResponse()

    if response_type == "price_found":
        price = payload.get("price")
        msg = f"The estimated cost for that repair is {price} dollars. Would you like help with anything else?"
        response.say(msg, voice="alice", language="en-US")
    
    elif response_type == "price_not_found":
        msg = "I don’t have an exact price for that repair right now. Could you please tell me the device model or the issue again?"
        response.say(msg, voice="alice", language="en-US")
    
    elif response_type == "pricing_restricted":
        msg = "Computer and laptop repairs require an in-store diagnostic. Please visit the store or call us during business hours for assistance."
        response.say(msg, voice="alice", language="en-US")
    
    else:
        # Default acknowledgment for unknown intents for now
        response.say("Thanks, one moment please.", voice="alice", language="en-US")
    
    # Keep the call alive
    response.pause(length=1) 
    
    return Response(content=str(response), media_type="application/xml")
