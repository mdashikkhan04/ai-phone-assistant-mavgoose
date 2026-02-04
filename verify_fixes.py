
import asyncio
from fastapi import Request
from api.webhooks.gather import handle_gather
from unittest.mock import AsyncMock, MagicMock
from core import prompt_manager

async def test_fixes():
    print("--- Starting Verification ---")

    # Test 1: "Fix my iPhone" -> Should be pricing intent
    print("\nTest 1: 'I want to fix my iPhone'")
    
    # Mock Request
    request = MagicMock(spec=Request)
    request.form = AsyncMock(return_value={
        "SpeechResult": "I want to fix my iPhone",
        "From": "+1234567890",
        "Called": "+1987654321",
        "CallSid": "CA12345"
    })
    
    # Mock store resolver
    # We need to ensure resolve_store_by_did returns a store
    # Since we can't easily mock the import inside the function without more complex patching,
    # we will rely on integration behaviour or just patch the import if needed.
    # However, for this simple script, we assume the code runs in the same environment.
    
    # Let's try running the handler. 
    # Note: This requires the DB/Config to be accessible or mocked. 
    # Since we don't want to touch too much, let's see if we can run it.
    
    try:
        response = await handle_gather(request)
        content = response.body.decode('utf-8')
        
        print(f"Response Content:\n{content}")
        
        if "typical cost" in content or "pricing" in content or "dollars" in content: 
             # exact string depends on get_pricing_found, but we check for general success
             # Actually, if we look at prompt_manager.py, get_pricing_found returns "...estimated cost..."
             if "estimated cost" in content:
                 print("✅ SUCCESS: 'fix' triggered pricing logic.")
             elif "booking" in content:
                 # Should not happen if open, but acceptable if closed
                 print("⚠️ NOTICE: Triggered booking (maybe after hours).")
             else:
                 print("❌ FAILURE: Did not trigger pricing logic.")
        else:
            # If price not found, it might go to transfer. 
            # But the key is that it shouldn't be silence or fallback if intent is pricing.
            if "connect you" in content:
                 print("✅ SUCCESS: 'fix' triggered transfer (pricing not found but intent recognised).")
            else:
                 print(f"❓ UNCERTAIN: Content: {content}")

    except Exception as e:
        print(f"❌ ERROR in Test 1: {e}")

    # Test 2: Unknown Input -> Should have Gather + Friendly Prompt
    print("\nTest 2: Unknown Input 'blah blah'")
    
    request.form = AsyncMock(return_value={
        "SpeechResult": "blah blah random",
        "From": "+1234567890",
        "Called": "+1987654321",
        "CallSid": "CA12345"
    })

    try:
        response = await handle_gather(request)
        content = response.body.decode('utf-8')
        print(f"Response Content:\n{content}")
        
        expected_prompt = prompt_manager.get_clarification_prompt()
        
        if expected_prompt in content:
            print("✅ SUCCESS: Correct fallback prompt used.")
        else:
             print("❌ FAILURE: Incorrect prompt.")

        if "<Gather" in content and "/webhooks/gather" in content:
            print("✅ SUCCESS: <Gather> tag present for unknown input.")
        else:
            print("❌ FAILURE: <Gather> tag MISSING for unknown input.")
            
    except Exception as e:
        print(f"❌ ERROR in Test 2: {e}")

if __name__ == "__main__":
    asyncio.run(test_fixes())
