import os
from loguru import logger
from twilio.rest import Client
from typing import Dict, Any, Optional

def get_twilio_credentials(store: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    Resolves Twilio credentials from environment variables based on store's env_prefix.
    """
    prefix = store.get("env_prefix")
    if not prefix:
        logger.error(f"Store {store.get('name')} missing env_prefix.")
        return {}

    account_sid = os.getenv(f"{prefix}_TWILIO_ACCOUNT_SID")
    auth_token = os.getenv(f"{prefix}_TWILIO_AUTH_TOKEN")
    from_number = os.getenv(f"{prefix}_TWILIO_FROM_NUMBER")

    return {
        "account_sid": account_sid,
        "auth_token": auth_token,
        "from_number": from_number
    }

def get_twilio_client(store: Dict[str, Any]) -> Optional[Client]:
    """
    Creates and returns a Twilio Client for the specific store.
    Returns None if credentials are missing.
    """
    creds = get_twilio_credentials(store)
    
    account_sid = creds.get("account_sid")
    auth_token = creds.get("auth_token")

    if not account_sid or not auth_token:
        logger.error(f"Missing Twilio credentials for store: {store.get('name')} (Prefix: {store.get('env_prefix')})")
        return None

    try:
        return Client(account_sid, auth_token)
    except Exception as e:
        logger.error(f"Failed to initialize Twilio Client for {store.get('name')}: {e}")
        return None
