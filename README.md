# LLM-Powered Prompt Router (Gemini-Powered)

An intelligent intent classification and routing service built with Python and Google Gemini. This system intelligently routes user requests to specialized AI "experts" based on the detected intent, ensuring accurate and context-aware responses.

## 🚀 Key Features
- **Intelligent Intent Classification**: Automatically categorizes queries into `coder`, `writer`, `analyst`, `coach`, or `unclear`.
- **Specialized Expert Routing**: Maps intents to custom-defined system prompts (personas) stored in `config.json`.
- **Built-in Robustness & Fallbacks**:
    - **Smart Fallback**: Automatically switches to a local keyword-based classifier if the API is down or quota is exceeded.
    - **Simulated Responses**: Provides persona-accurate simulated responses during API outages.
- **Audit Logging**: Every transaction is logged to a JSON Lines file (`route_log.jsonl`) for tracking and performance monitoring.
- **JSON Validation**: Ensures all AI-generated intents conform to a strict schema.

## 📁 Project Structure
- `router.py`: The core engine containing classification and routing logic.
- `app.py`: Interactive CLI application for live testing.
- `config.json`: Configurable expert personas and system prompts.
- `test_router.py`: Comprehensive test suite (supports mocking for zero-cost testing).
- `requirements.txt`: Project dependencies.
- `.env.example`: Template for environment variables.

## 🛠️ Setup Instructions

### 1. Prerequisite: Get a Gemini API Key
Visit [Google AI Studio](https://aistudio.google.com/) and create a free API key.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory and add your key:
```text
GOOGLE_API_KEY=your_key_here
```

## 🎮 Usage Guide

### Run Interactive Demo
Experience the router in real-time:
```bash
python app.py
```

### Run Automated Tests
Verify logic and fallback mechanisms:
```bash
python test_router.py
```

### Quick Terminal Test
Run a quick test directly from your command line:
```bash
python -c "from router import route_and_respond; print(route_and_respond('How do I fix a bug in Python?'))"
```

### Integration in Your Code
To use the router in your own Python script (`main.py`):
```python
from router import route_and_respond

user_msg = "How do I create a list in Python?"
response = route_and_respond(user_msg)
print(response)
```

## 🧠 Behind the Scenes
The project follows a "Receptionist & Expert" architecture. The `classify_intent` function acting as the receptionist identifies the goal, and `route_and_respond` walks the user to the correct expert room. The local fallback ensures that even without an internet connection or API credits, the logic remains sound.
