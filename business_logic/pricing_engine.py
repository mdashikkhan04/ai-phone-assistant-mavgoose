from utils.backend_client import backend_client
from loguru import logger

# SOP: Map common speech terms to normalized database keys
# This map helps bridge the gap between AI's detected issue and backend's repair_type name
ISSUE_MAP = {
    "screen": ["glass_lcd", "glass", "lcd", "screen repair", "screen replacement"],
    "battery": ["battery", "battery replacement"],
    "charging": ["dock", "charging port"],
    "port": ["dock", "charging port"],
    "hdmi": ["hdmi", "hdmi port"]
}

def get_repair_price(store_id: int, device_category: str, model: str, issue: str) -> dict | None:
    """
    Look up repair prices from the backend for a specific store.
    """
    try:
        # Fetch prices for this store from the backend
        prices = backend_client.get_price_list(store_id)
        if not prices:
            return None

        issue_lower = issue.lower()
        model_lower = model.lower()
        
        # Filter logic
        # Prices from backend usually have fields like:
        # { "device_model_name": "iPhone 13", "repair_type_name": "Screen Replacement", "price": "129.99" }
        
        possible_repairs = ISSUE_MAP.get(issue_lower, [issue_lower])
        
        for item in prices:
            item_model = str(item.get("device_model_name", "")).lower()
            item_repair = str(item.get("repair_type_name", "")).lower()
            
            # Simple fuzzy/exact matching for model and repair type
            if model_lower in item_model or item_model in model_lower:
                # Check if repair type matches
                if any(rep in item_repair for rep in possible_repairs):
                    return {
                        "price": float(item.get("price", 0)),
                        "currency": "USD",
                        "repair_type": item.get("repair_type_name"),
                        "model": item.get("device_model_name")
                    }

    except Exception as e:
        logger.error(f"Error resolving dynamic price: {e}")
    
    return None
