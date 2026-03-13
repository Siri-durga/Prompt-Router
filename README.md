# LLM-Powered Prompt Router

An intelligent intent classification and routing service powered by Google Gemini (Free Tier).

## Features
- **Intent Classification**: Categorizes user messages into 'coder', 'writer', 'analyst', 'coach', or 'unclear'.
- **Expert Routing**: Routes requests to specialized expert personas.
- **JSONL Logging**: Logs all transactions to `route_log.jsonl`.
- **Robustness**: Gracefully handles API errors and malformed LLM responses.

## Setup
1.  **Clone the repository**.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure API Key**:
    - Get a free key from [aistudio.google.com](https://aistudio.google.com/).
    - Create a `.env` file:
    ```text
    GOOGLE_API_KEY=your_gemini_api_key_here
    ```

## Usage
Run the test suite to verify everything is working:
```bash
python test_router.py
```

Import and use in your code:
```python
from router import route_and_respond
response = route_and_respond("How do I write a Python function?")
print(response)
```
