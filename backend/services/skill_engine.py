import json
from backend.services.llm_engine import analyze_code_with_llm


def analyze_skill(language: str, code: str, diagnostics: str | None = None):
    llm_response = analyze_code_with_llm(language, code, diagnostics)

    try:
        parsed = json.loads(llm_response)
    except json.JSONDecodeError:
        raise ValueError("LLM response is not valid JSON")

    return {
        "language": language,
        "strengths": parsed.get("strengths", []),
        "skill_gaps": parsed.get("skill_gaps", []),
        "suggestions": parsed.get("suggestions", []),
        "confidence_score": parsed.get("confidence_score", 0)
    }
