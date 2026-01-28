import json
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parents[1]
PRICING_DIR = BASE_DIR / "data" / "pricing"

CATEGORY_MAP = {
    "phone": "phones.json",
    "tablet": "tablets.json",
    "console": "consoles.json"
}

# SOP: Map common speech terms to normalized database keys
ISSUE_MAP = {
    "screen": ["glass_lcd", "glass", "lcd"],
    "battery": ["battery"],
    "charging": ["dock"],
    "port": ["dock"],
    "hdmi": ["hdmi", "dock"]
}

def get_repair_price(device_category: str, model: str, issue: str) -> dict | None:
    """
    Look up repair prices from static JSON files using exact and mapped matching.
    """
    filename = CATEGORY_MAP.get(device_category.lower())
    if not filename:
        return None
    
    file_path = PRICING_DIR / filename
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "r") as f:
            pricing_data = json.load(f)
        
        # Exact model matching (case-insensitive)
        stored_model = None
        for key in pricing_data.keys():
            if key.lower() == model.lower():
                stored_model = key
                break
        
        if stored_model:
            model_data = pricing_data[stored_model]
            issue_lower = issue.lower()
            
            # 1. Try direct matching
            for issue_name, price in model_data.items():
                if issue_name.lower() == issue_lower:
                    return {"price": price, "currency": "USD"}
            
            # 2. Try mapped matching (e.g. "screen" -> "glass_lcd")
            target_keys = ISSUE_MAP.get(issue_lower, [])
            for target in target_keys:
                if target in model_data:
                    return {"price": model_data[target], "currency": "USD"}

    except Exception as e:
        print(f"Error reading pricing data: {e}")
    
    return None
