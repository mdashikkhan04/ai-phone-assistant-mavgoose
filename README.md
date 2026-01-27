# AI Voice Agent for Multi-Location Phone Repair

This project is a production-ready AI Voice Agent designed to handle incoming calls for a multi-location phone repair business. It provides repair pricing, manages after-hours bookings via SMS, and performs warm transfers to store staff during business hours.

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.9+
- Twilio Account (SID, Auth Token, and a Twilio Phone Number)
- Publicly accessible server or tunneling tool like `ngrok`

### 2. Installation
```bash
# Clone the repository
git clone <repository-url>
cd ai-phone-assistant

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=your_twilio_phone_number
```

### 4. Running the Application
```bash
# Start the FastAPI server
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## 🛠 Twilio Configuration

To connect Twilio to your backend:
1.  **Voice Webhook**: Set the "A CALL COMES IN" URL to `https://<your-domain>/webhooks/voice`.
2.  **Ensure POST**: Set the method to `POST`.

## 🧪 Test Scenarios

### In-Hours (10 AM - 7 PM EST)
- **Pricing Request**: Ask "How much to fix an iPhone 13 screen?" -> Expect a specific price.
- **Complex Issue**: Say "I have water damage on my phone." -> Expect a warm transfer to store staff.
- **Direct Transfer**: Say "Talk to a technician." -> Expect a warm transfer.

### After-Hours
- **Any Pricing/Booking Request**: -> Expect an offer for an SMS booking link.
- **Consent Flow**: Say "Yes" to the booking offer -> Expect an SMS with the store-specific booking URL.

### Policy Enforcement
- **Computer Repair**: Ask "How much for a MacBook screen repair?" -> Expect a polite redirection to visit the store.

## 📋 Deployment Checklist

- [ ] Verify `.env` credentials are correct.
- [ ] Ensure `data/stores/stores.json` contains valid `phone_number` and `transfer_number`.
- [ ] Ensure `data/booking_links.json` has the correct URLs for each `store_id`.
- [ ] Test the business hours logic in `utils/time_utils.py` by mocking the system time.
- [ ] Confirm Twilio webhooks are pointing to the correct production URL.
- [ ] Verify that `data/logs/` is writable for `call_logs.py`.

## 📂 Project Structure

- `api/`: Webhook endpoints (`inbound_call.py`, `gather.py`).
- `core/`: Orchestration logic (`state_machine.py`, `prompt_manager.py`, `store_resolver.py`).
- `business_logic/`: Deterministic rules (`pricing_engine.py`, `hours_validator.py`).
- `actions/`: Outbound services (`sms_service.py`, `transfer_service.py`).
- `data/`: JSON data stores for pricing, stores, and booking links.
- `database/`: Call event logging.
- `utils/`: Shared utilities (time, logging).
