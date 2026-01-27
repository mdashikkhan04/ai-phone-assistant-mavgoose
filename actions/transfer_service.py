import os
import time
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Twilio Credentials
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def initiate_warm_transfer(customer_call_sid: str, store_phone_number: str, briefing_text: str):
    """
    Executes a warm transfer:
    1. Puts customer on hold (Twilio hold music).
    2. Dials store_phone_number.
    3. Plays briefing_text to staff when they answer.
    4. Bridges customer and staff together in a conference.
    """
    try:
        if not ACCOUNT_SID or not AUTH_TOKEN:
            print("ERROR: Twilio credentials missing.")
            return False

        conference_name = f"conf_{customer_call_sid}"
        
        # 1. Update customer call to join conference with hold music
        print(f"LOG: Moving customer {customer_call_sid} to conference {conference_name}")
        client.calls(customer_call_sid).update(
            twiml=f'<Response><Dial><Conference waitUrl="http://twimlets.com/holdmusic?Bucket=com.twilio.music.classical">{conference_name}</Conference></Dial></Response>'
        )
        
        # 2. Call the store staff
        # We use 'twiml' parameter to play the briefing before they join the conference
        print(f"LOG: Calling store at {store_phone_number} with briefing: {briefing_text}")
        staff_call = client.calls.create(
            to=store_phone_number,
            from_=FROM_NUMBER,
            timeout=20,  # Staff must answer within 20 seconds
            twiml=f'<Response><Say voice="alice">{briefing_text}</Say><Dial><Conference>{conference_name}</Conference></Dial></Response>'
        )
        
        # 3. Simple polling to detect if the call was answered or failed immediately
        # We check for a few seconds to see if it's 'in-progress'. 
        # If it's 'failed', 'busy', or 'no-answer', we return failure.
        start_time = time.time()
        while time.time() - start_time < 22:
            try:
                updated_call = client.calls(staff_call.sid).fetch()
                if updated_call.status in ['in-progress', 'completed']:
                    return True
                if updated_call.status in ['failed', 'busy', 'no-answer', 'canceled']:
                    print(f"LOG: Staff call failed with status: {updated_call.status}")
                    return False
            except Exception as poll_err:
                print(f"LOG: Polling error: {poll_err}")
            
            time.sleep(1)
            
        print("LOG: Staff call timed out or remained in queued/ringing state.")
        return False
        
    except Exception as e:
        print(f"Transfer Error: {e}")
        return False
