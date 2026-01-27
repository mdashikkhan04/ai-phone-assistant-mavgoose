import json
import os
from datetime import datetime
from pathlib import Path

# Path for the logs file
BASE_DIR = Path(__file__).resolve().parents[1]
LOGS_DIR = BASE_DIR / "data" / "logs"
LOGS_FILE = LOGS_DIR / "call_events.json"

# Ensure data/logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

def log_call_event(data: dict):
    """
    Logs a call event to a JSON file.
    Expected data fields:
    - call_sid
    - store_id
    - intent
    - response_type
    - pricing_found (bool)
    - sms_sent (bool)
    - transfer_attempted (bool)
    """
    event = {
        "call_sid": data.get("call_sid"),
        "store_id": data.get("store_id"),
        "intent": data.get("intent"),
        "response_type": data.get("response_type"),
        "pricing_found": data.get("pricing_found", False),
        "sms_sent": data.get("sms_sent", False),
        "transfer_attempted": data.get("transfer_attempted", False),
        "created_at": datetime.utcnow().isoformat()
    }

    print(f"DEBUG LOG: {json.dumps(event, indent=2)}")

    # Persistence to JSON file
    logs = []
    if LOGS_FILE.exists():
        try:
            with open(LOGS_FILE, "r") as f:
                logs = json.load(f)
        except:
            logs = []
    
    logs.append(event)
    
    with open(LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=4)
