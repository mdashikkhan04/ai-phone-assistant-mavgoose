from fastapi import APIRouter, Response, Request
from twilio.twiml.voice_response import VoiceResponse
from core.store_resolver import resolve_store_by_did
from core import prompt_manager

router = APIRouter()

@router.post("/voice")
async def handle_inbound_call(request: Request):
    """
    Handles incoming calls from Twilio, detects store, and greets.
    """
    # Extract the called number (DID) from Twilio request
    form_data = await request.form()
    called_number = form_data.get("Called", "")
    
    # Resolve store
    store = resolve_store_by_did(called_number)
    store_id = store.get("id")
    
    # Dynamic greeting from prompt_manager
    greeting = prompt_manager.get_greeting(
        store.get("name"), 
        store.get("location"), 
        store_id=store_id
    )
    
    response = VoiceResponse()
    
    # Gather speech from the caller
    response.say(
    greeting,
    voice="Polly.Joanna",
    language="en-US"
    )

    response.gather(
    input="speech",
    action="/webhooks/gather",
    method="POST",
    speech_timeout="5"
    )

    return Response(content=str(response), media_type="application/xml")
