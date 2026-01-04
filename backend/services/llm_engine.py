# backend/services/llm_engine.py
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

def analyze_code_with_llm(language: str, code: str, diagnostics: str | None = None):
    prompt = f"""
You are a technical skill evaluator.

Analyze the following {language} code and respond ONLY in valid JSON.

JSON format:
{{
  "strengths": [],
  "skill_gaps": [],
  "suggestions": [],
  "confidence_score": 0
}}

Code:
{code}
"""

    # ✅ Use alias that always works for your key
    model_name = "gemini-flash-latest"  # ← resolves to e.g., gemini-2.0-flash-001

    # Build URL safely (no spaces)
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{model_name}:generateContent?key={API_KEY}"
    )

    print(f"🔍 Calling: .../{model_name}:generateContent?key=...{API_KEY[-4:]}")

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    }

    for attempt in range(3):
        try:
            r = requests.post(url, json=data, timeout=30)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"]
            
            elif r.status_code == 429:
                wait = 2 ** attempt
                print(f"⚠️ Quota limit. Retrying in {wait}s...")
                time.sleep(wait)
            
            else:
                err = r.json().get("error", {}).get("message", r.text[:200])
                raise RuntimeError(f"❌ {r.status_code}: {err}")

        except requests.RequestException as e:
            if attempt == 2:
                raise RuntimeError(f"Network error: {e}")
            time.sleep(1)

    raise RuntimeError("Max retries exceeded")