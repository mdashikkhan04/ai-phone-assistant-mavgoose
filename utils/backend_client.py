import os
import requests
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_API_TOKEN = os.getenv("BACKEND_API_TOKEN", "")

class BackendClient:
    def __init__(self):
        self.base_url = BACKEND_URL.rstrip("/")
        self.session = requests.Session()
        if BACKEND_API_TOKEN:
            self.session.headers.update({"Authorization": f"Bearer {BACKEND_API_TOKEN}"})

    def get_stores(self):
        """Fetch list of all stores from the backend."""
        try:
            url = f"{self.base_url}/api/v1/stores/"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch stores: {e}")
            return []

    def get_price_list(self, store_id: int):
        """Fetch price list for a specific store."""
        try:
            url = f"{self.base_url}/api/v1/services/price-list/"
            params = {"store": store_id}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch price list for store {store_id}: {e}")
            return []

    def log_call_event(self, call_data: dict):
        """Post call log event to the backend."""
        try:
            url = f"{self.base_url}/api/v1/call/"
            response = self.session.post(url, json=call_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to log call event: {e}")
            return None

    def get_ai_behavior(self, store_id: int):
        """Fetch AI behavior configuration for a store."""
        try:
            url = f"{self.base_url}/api/v1/stores/{store_id}/ai-behavior/"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch AI behavior for store {store_id}: {e}")
            return None

    def get_available_slots(self, store_id: int):
        """Fetch available appointment slots for a store."""
        try:
            url = f"{self.base_url}/api/v1/appointments/stores/{store_id}/available-slots/"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch slots for store {store_id}: {e}")
            return []

    def book_appointment(self, appointment_data: dict):
        """Book an appointment on the backend."""
        try:
            url = f"{self.base_url}/api/v1/appointments/book/"
            response = self.session.post(url, json=appointment_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to book appointment: {e}")
            return None

backend_client = BackendClient()
