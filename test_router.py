import json
import os
from unittest.mock import MagicMock, patch

# Mock API key before importing router to prevent initialization errors
with patch.dict(os.environ, {"GOOGLE_API_KEY": "sk-mock-key"}):
    from router import classify_intent, route_and_respond, LOG_FILE

def test_classification_malformed_json():
    """Verifies that malformed JSON from Gemini results in an 'unclear' intent."""
    print("\n--- Testing Malformed JSON Handling ---")
    
    with patch("router.get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = "This is not JSON"
        # In the new SDK, it's client.models.generate_content
        mock_client.models.generate_content.return_value = mock_response

        result = classify_intent("Hello")
        print(f"Result for malformed JSON: {result}")
        assert result["intent"] == "unclear"
        assert result["confidence"] == 0.0
    print("Test Passed: Malformed JSON handled correctly.")

def test_unclear_intent_routing():
    """Verifies that 'unclear' intent returns a clarification question."""
    print("\n--- Testing 'unclear' Intent Routing ---")
    
    with patch("router.classify_intent") as mock_classify:
        mock_classify.return_value = {"intent": "unclear", "confidence": 0.0}
        
        response = route_and_respond("Random gibberish")
        print(f"Response for 'unclear': {response}")
        assert "Are you asking for help with coding, data analysis, writing, or career advice?" in response
    print("Test Passed: 'unclear' intent provides clarification.")

def test_logging():
    """Verifies that transactions are logged to route_log.jsonl."""
    print("\n--- Testing Logging ---")
    
    # Clear log file if it exists
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        
    with patch("router.classify_intent") as mock_classify:
        mock_classify.return_value = {"intent": "coder", "confidence": 0.95}
        
        with patch("router.get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.text = "Here is some code."
            mock_client.models.generate_content.return_value = mock_response
            
            route_and_respond("Write a function")
            
    assert os.path.exists(LOG_FILE)
    with open(LOG_FILE, "r") as f:
        log_data = json.loads(f.readline())
        print(f"Logged entry: {log_data}")
        assert log_data["intent"] == "coder"
        assert log_data["user_message"] == "Write a function"
        assert log_data["final_response"] == "Here is some code."
    print("Test Passed: Log file created and formatted correctly.")

if __name__ == "__main__":
    try:
        test_classification_malformed_json()
        test_unclear_intent_routing()
        test_logging()
        print("\nAll tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
