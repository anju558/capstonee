from typing import Dict, List

from backend.services.skill_state_service import (
    get_user_skill_states,
    compute_skill_gap
)
from backend.services.skill_summary import generate_skill_report
from backend.ml.models import predict_mastery


# -------------------------------------------------
# 🔒 HARD SAFETY FILTER
# -------------------------------------------------
def is_valid_skill(skill: str) -> bool:
    if not skill:
        return False

    skill = skill.strip().lower()

    # Reject sentences
    if len(skill.split()) > 3:
        return False

    # Reject diagnostics / punctuation
    if any(c in skill for c in [":", ".", "(", ")", ",", "'"]):
        return False

    return True


def normalize_level(level: int) -> float:
    """
    Convert level (1–5) → percentage (0–100)
    """
    return round((level / 5) * 100, 2)


def merge_confidence_and_state(
    state: Dict,
    event_summary: Dict
) -> Dict:
    skill = state["skill"].lower()

    event_conf = event_summary.get(skill, {}).get(
        "confidence_score", 50
    )

    state_conf = normalize_level(state["current_level"])

    # 🎯 Weighted fusion
    final_confidence = round(
        (0.6 * state_conf) + (0.4 * event_conf),
        2
    )

    mastery = predict_mastery(final_confidence)

    gap = state["target_level"] - state["current_level"]

    return {
        "skill": skill,
        "current_level": state["current_level"],
        "target_level": state["target_level"],
        "gap": gap,
        "priority": "HIGH" if gap >= 3 else "MEDIUM" if gap == 2 else "LOW",
        "event_confidence": event_conf,
        "state_confidence": state_conf,
        "final_confidence": final_confidence,
        "mastery": mastery,
        "recommendation": event_summary.get(
            skill,
            {}
        ).get("recommendation", "Keep practicing")
    }


# -------------------------------------------------
# 🚀 FINAL SKILL PROFILE API
# -------------------------------------------------
async def get_merged_skill_profile(user_id: str) -> List[Dict]:
    skill_states = await get_user_skill_states(user_id)
    event_summary = await generate_skill_report(user_id)

    merged: List[Dict] = []

    for state in skill_states:
        if not is_valid_skill(state.get("skill")):
            continue

        enriched = compute_skill_gap(state)

        merged.append(
            merge_confidence_and_state(
                enriched,
                event_summary
            )
        )

    merged.sort(key=lambda x: x["gap"], reverse=True)

    return merged
