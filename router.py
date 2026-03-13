import json
import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Configuration
CONFIG_FILE = "config.json"
LOG_FILE = "route_log.jsonl"

def load_config() -> Dict[str, Any]:
    """Loads the configuration from a JSON file."""
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

# Global client reference
_client = None

def get_client():
    """Returns a singleton Gemini Client, initializing it if necessary."""
    global _client
    if _client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("GOOGLE_API_KEY not found. Please create a .env file with your key from aistudio.google.com.")
        
        _client = genai.Client(api_key=api_key)
        
    return _client

def log_transaction(intent: str, confidence: float, user_message: str, final_response: str):
    """Logs the routing decision and response to a JSONLines file."""
    log_entry = {
        "intent": intent,
        "confidence": confidence,
        "user_message": user_message,
        "final_response": final_response
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def local_classify_intent(user_message: str) -> Dict[str, Any]:
    """
    A rule-based fallback classifier that works without an API key.
    Useful when API quota is exhausted.
    """
    msg = user_message.lower()
    
    # Simple keyword mapping
    keywords = {
        "coder": ["code", "python", "script", "debug", "error", "function", "programming", "software", "java", "html", "css", "javascript"],
        "writer": ["write", "email", "story", "poem", "essay", "edit", "grammar", "style", "letter", "blog"],
        "analyst": ["data", "chart", "statistic", "analysis", "business", "logic", "excel", "sql", "math", "plus", "+", "-", "*", "/", "=", "count", "sum", "total"] + [str(i) for i in range(10)],
        "coach": ["career", "job", "interview", "advice", "goal", "management", "time", "motivation", "resume", "skills"]
    }
    
    for intent, words in keywords.items():
        if any(word in msg for word in words):
            return {"intent": intent, "confidence": 0.5}
            
    return {"intent": "unclear", "confidence": 0.0}

def classify_intent(user_message: str) -> Dict[str, Any]:
    """
    Calls Gemini to classify user intent.
    Falls back to local keyword classification on API failure/quota issues.
    """
    config = load_config()
    classification_prompt = config["classification_prompt"].format(message=user_message)

    try:
        client = get_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=classification_prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        content = response.text
        result = json.loads(content)
        
        # Validate schema
        if "intent" not in result or "confidence" not in result:
             raise ValueError("Malformed response schema")
             
        return result
    except Exception as e:
        print(f"Note: API Classification unavailable ({e}). Using local fallback.")
        return local_classify_intent(user_message)

def local_generate_response(intent: str, user_message: str) -> str:
    """
    Generates a simulated response based on the expert persona.
    Used when API quota is exhausted.
    """
    config = load_config()
    expert = config["experts"].get(intent)
    if not expert:
        return "I'm not sure how to help with that. Could you clarify your request?"
        
    persona = expert["persona"]
    return (f"[SIMULATED RESPONSE - API QUOTA EXCEEDED]\n"
            f"Based on my persona as: {persona}\n\n"
            f"I understand you are asking about: '{user_message}'. "
            f"I would typically provide a detailed {intent}-related answer here. "
            f"Please check your API quota at ai.google.dev to see my real AI brain in action!")

def route_and_respond(user_message: str) -> str:
    """
    Classifies intent, routes to the appropriate expert, and generates a response.
    Falls back to local logic if the API is unavailable.
    """
    config = load_config()
    classification = classify_intent(user_message)
    intent = classification["intent"]
    confidence = classification["confidence"]

    if intent == "unclear":
        final_response = "I'm not exactly sure how to help with that. Are you asking for help with coding, data analysis, writing, or career advice?"
    elif intent in config["experts"]:
        expert = config["experts"][intent]
        system_prompt = expert["persona"]
        
        try:
            client = get_client()
            # Send system prompt as part of the content
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"System: {system_prompt}\n\nUser: {user_message}"
            )
            final_response = response.text
        except Exception as e:
            print(f"Note: API Generation unavailable ({e}). Using local fallback.")
            final_response = local_generate_response(intent, user_message)
    else:
        # Unexpected intent fallback
        final_response = "That's an interesting request. Could you clarify if you need help with coding, writing, analysis, or coaching?"
        intent = "unclear"
        confidence = 0.0

    # Log the interaction
    log_transaction(intent, confidence, user_message, final_response)
    
    return final_response

if __name__ == "__main__":
    # Example usage
    test_input = "Can you help me write a Python script for web scraping?"
    print(f"User: {test_input}")
    try:
        print(f"Response: {route_and_respond(test_input)}")
    except Exception as e:
        print(f"Error: {e}")
