import os
import time
import requests
from dotenv import load_dotenv

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not set")

MODEL_NAME = "gemini-flash-latest"
BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    f"models/{MODEL_NAME}:generateContent?key={API_KEY}"
)

HEADERS = {
    "Content-Type": "application/json"
}


# -------------------------------------------------
# 🔹 INTERNAL HELPER
# -------------------------------------------------
def _call_gemini(prompt: str) -> str:
    """
    Centralized Gemini API caller with retry + safety
    """
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    for attempt in range(3):
        try:
            response = requests.post(
                BASE_URL,
                headers=HEADERS,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]

            if response.status_code == 429:
                time.sleep(2 ** attempt)
                continue

            raise RuntimeError(response.text)

        except requests.RequestException as e:
            if attempt == 2:
                raise RuntimeError(f"Gemini API failed: {e}")

    raise RuntimeError("Gemini failed after retries")


# -------------------------------------------------
# 🔹 SKILL ANALYSIS (used by /api/analyze/code)
# -------------------------------------------------
def analyze_code_with_llm(
    language: str,
    code: str,
    diagnostics: str | None = None
) -> str:
    prompt = f"""
You are a JSON-only API.

RULES:
- Respond ONLY with valid JSON
- No markdown
- No explanation
- No extra text

JSON schema:
{{
  "strengths": [],
  "skill_gaps": [],
  "suggestions": [],
  "confidence_score": 0
}}

Analyze this {language} code:

{code}
"""

    if diagnostics:
        prompt += f"\nDiagnostics:\n{diagnostics}"

    return _call_gemini(prompt)


# -------------------------------------------------
# 🔹 RAG GENERATION (used by /api/rag/ask)
# -------------------------------------------------
def generate_answer(question: str, context: str) -> str:
    prompt = f"""
You are a helpful AI assistant.

Use ONLY the information provided in the context.
If the answer is not present, say: "I don't know based on the given context."

Context:
{context}

Question:
{question}
"""

    return _call_gemini(prompt)
