import json
import re
from backend.services.llm_engine import analyze_code_with_llm


def extract_json(text: str):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass

    return {
        "has_error": False,
        "confidence_score": 50,
        "simple_explanation": "AI temporarily unavailable.",
        "corrected_code": "",
        "next_steps": []
    }


def analyze_skill(language: str, code: str, combined_context: str = ""):
    print(">>> analyze_skill CALLED")

    llm_response = analyze_code_with_llm(
        language=language,
        code=code,
        combined_context=combined_context
    )

    parsed = extract_json(llm_response)

    return {
        "has_error": bool(parsed.get("has_error", False)),
        "confidence_score": int(parsed.get("confidence_score", 50)),
        "simple_explanation": str(parsed.get("simple_explanation", "")),
        "corrected_code": str(parsed.get("corrected_code", "")) if parsed.get("has_error") else "",
        "next_steps": parsed.get("next_steps", [])
        if isinstance(parsed.get("next_steps"), list) else []
    }
