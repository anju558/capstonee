import os
import json
import re
import time
import requests
from typing import Optional
from dotenv import load_dotenv

# =================================================
# 🔐 LOAD ENVIRONMENT
# =================================================

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"
BASE_URL = "https://generativelanguage.googleapis.com/v1/models/"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 30
MAX_RETRIES = 2


# =================================================
# 🔹 SAFE JSON FALLBACK
# =================================================

def _safe_json(message: str) -> str:
    return json.dumps({
        "has_error": False,
        "confidence_score": 50,
        "simple_explanation": message,
        "corrected_code": "",
        "next_steps": []
    })


# =================================================
# 🔹 GEMINI REQUEST HANDLER
# =================================================

def _make_gemini_request(prompt: str) -> Optional[str]:

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    url = f"{BASE_URL}{MODEL_NAME}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(
                url,
                headers=HEADERS,
                json=payload,
                timeout=TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])

                if not candidates:
                    return None

                content = candidates[0].get("content", {})
                parts = content.get("parts", [])

                if not parts:
                    return None

                return parts[0].get("text")

            if 500 <= response.status_code < 600:
                if attempt < MAX_RETRIES:
                    time.sleep(2)
                    continue

            return None

        except requests.Timeout:
            if attempt < MAX_RETRIES:
                time.sleep(2)
                continue
            return None

        except requests.RequestException:
            return None

    return None


# =================================================
# 🔹 JSON CLEANER
# =================================================

def _extract_valid_json(raw_text: str) -> Optional[dict]:

    if not raw_text:
        return None

    cleaned = raw_text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"```json|```", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


# =================================================
# 🔹 MAIN ANALYSIS
# =================================================

def analyze_code_with_llm(
    language: str,
    code: str,
    combined_context: str = ""
) -> str:

    prompt = f"""
You are a VS Code AI coding assistant.

STRICT RULES:
- Keep explanation under 4 short lines.
- Use simple beginner-friendly language.
- No long paragraphs.
- Maximum 3 next_steps only.
- Be direct and concise.
- No markdown formatting.

Respond ONLY in valid JSON:

{{
  "has_error": false,
  "confidence_score": 0,
  "simple_explanation": "",
  "corrected_code": "",
  "next_steps": []
}}

Context:
{combined_context}

Code ({language}):
{code}
"""

    raw_output = _make_gemini_request(prompt)

    if not raw_output:
        return _safe_json("AI response unavailable.")

    parsed_json = _extract_valid_json(raw_output)

    if not parsed_json:
        return _safe_json("AI response parsing failed.")

    # ✅ LIMIT NEXT STEPS TO 3 (ONLY NEW LOGIC ADDED)
    if "next_steps" in parsed_json and isinstance(parsed_json["next_steps"], list):
        parsed_json["next_steps"] = parsed_json["next_steps"][:3]

    return json.dumps(parsed_json)


# =================================================
# 🔹 CHAT MODE
# =================================================

def generate_answer(question: str, context: str) -> str:

    prompt = f"""
You are a VS Code coding assistant.

Rules:
- Answer in maximum 5 short lines.
- Be clear and direct.
- Avoid long theoretical explanations.
- No markdown.
- No headings.

Context:
{context}

User Question:
{question}
"""

    raw_output = _make_gemini_request(prompt)

    if not raw_output:
        return "AI temporarily unavailable."

    cleaned = raw_output.strip()

    # 🔥 Force maximum 6 lines
    lines = cleaned.splitlines()
    shortened = "\n".join(lines[:6])

    return shortened