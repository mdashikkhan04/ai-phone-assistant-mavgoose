from utils.backend_client import backend_client

DEFAULT_STORE = {
    "store_id": "default",
    "name": "our store",
    "did": "default",
    "location": "your local area"
}

def resolve_store_by_did(called_number: str) -> dict:
    """
    Look up a store based on the incoming phone number (DID) from the backend.
    """
    try:
        stores = backend_client.get_stores()
        
        for store in stores:
            # Backend stores have 'did_number' or similar? 
            # Let's check backend serializer for Store model.
            if store.get("did") == called_number or store.get("phone_number") == called_number:
                return store
    except Exception as e:
        print(f"Error resolving store: {e}")
        return DEFAULT_STORE

    return DEFAULT_STORE
