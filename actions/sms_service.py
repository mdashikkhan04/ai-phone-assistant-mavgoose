import os
from twilio.rest import Client

def send_booking_sms(to_number: str, booking_url: str):
    """
    Sends a booking link to the customer via Twilio SMS.
    """
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_FROM_NUMBER")

    if not all([account_sid, auth_token, from_number]):
        print("ERROR: Twilio credentials missing from environment.")
        return

    client = Client(account_sid, auth_token)

    message_body = f"You can book your appointment here: {booking_url}"

    try:
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        print(f"SMS Sent successfully: {message.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")
