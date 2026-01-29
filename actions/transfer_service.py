import time
from typing import Dict, Any
from utils.twilio_utils import get_twilio_client, get_twilio_credentials
from loguru import logger

def initiate_warm_transfer(customer_call_sid: str, store_phone_number: str, briefing_text: str, store: Dict[str, Any]):
    """
    Executes a warm transfer using store-specific Twilio credentials:
    1. Puts customer on hold (Twilio hold music).
    2. Dials store_phone_number.
    3. Plays briefing_text to staff when they answer.
    4. Bridges customer and staff together in a conference.
    """
    try:
        client = get_twilio_client(store)
        creds = get_twilio_credentials(store)
        from_number = creds.get("from_number")

        if not client or not from_number:
            logger.error(f"Cannot initiate transfer: Twilio credentials missing for {store.get('name')}")
            return False

        conference_name = f"conf_{customer_call_sid}"
        
        # 1. Update customer call to join conference with hold music
        logger.info(f"Moving customer {customer_call_sid} to conference {conference_name} via {store.get('name')} account")
        client.calls(customer_call_sid).update(
            twiml=f'<Response><Dial><Conference waitUrl="http://twimlets.com/holdmusic?Bucket=com.twilio.music.classical">{conference_name}</Conference></Dial></Response>'
        )
        
        # 2. Call the store staff
        logger.info(f"Calling store {store.get('name')} staff at {store_phone_number} with briefing: {briefing_text}")
        staff_call = client.calls.create(
            to=store_phone_number,
            from_=from_number,
            timeout=20,  # Staff must answer within 20 seconds
            twiml=f'<Response><Say voice="alice">{briefing_text}</Say><Dial><Conference>{conference_name}</Conference></Dial></Response>'
        )
        
        # 3. Simple polling to detect if the call was answered or failed immediately
        start_time = time.time()
        while time.time() - start_time < 22:
            try:
                updated_call = client.calls(staff_call.sid).fetch()
                if updated_call.status in ['in-progress', 'completed']:
                    logger.success(f"Staff call for {store.get('name')} answered.")
                    return True
                if updated_call.status in ['failed', 'busy', 'no-answer', 'canceled']:
                    logger.warning(f"Staff call for {store.get('name')} failed with status: {updated_call.status}")
                    return False
            except Exception as poll_err:
                logger.error(f"Polling error for {store.get('name')}: {poll_err}")
            
            time.sleep(1)
            
        logger.warning(f"Staff call for {store.get('name')} timed out or remained in queued/ringing state.")
        return False
        
    except Exception as e:
        logger.error(f"Transfer Error for {store.get('name')}: {e}")
        return False
