import json
import re
from backend.services.llm_engine import analyze_code_with_llm



def extract_json(text: str):
    """
    Extract JSON object from LLM output safely
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
        raise ValueError("No valid JSON found in LLM response")


def analyze_skill(language: str, code: str, diagnostics: str | None = None):
    llm_response = analyze_code_with_llm(language, code, diagnostics)

    parsed = extract_json(llm_response)

    return {
        "language": language,
        "strengths": parsed.get("strengths", []),
        "skill_gaps": parsed.get("skill_gaps", []),
        "suggestions": parsed.get("suggestions", []),
        "confidence_score": parsed.get("confidence_score", 0),
    }
