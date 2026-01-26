import json
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parents[1]  # project root
STORES_FILE = BASE_DIR / "data" / "stores" / "stores.json"

DEFAULT_STORE = {
    "store_id": "default",
    "name": "our store",
    "phone_number": "default",
    "location": "your local area"
}

def resolve_store(called_number: str) -> dict:
    """
    Look up a store based on the incoming phone number (DID).
    """
    if not os.path.exists(STORES_FILE):
        return DEFAULT_STORE

    try:
        with open(STORES_FILE, "r") as f:
            stores = json.load(f)
        
        for store in stores:
            if store.get("phone_number") == called_number:
                return store
    except Exception as e:
        # For now, fail silently but future logging can be added
        return DEFAULT_STORE

    return DEFAULT_STORE
