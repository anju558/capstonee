def compute_confidence(skill_data):
    confidence = 100

    confidence -= skill_data.get("gaps_detected", 0) * 10
    confidence -= skill_data.get("avg_difficulty", 0) * 5
    confidence += skill_data.get("attempts", 0) * 2

    return max(0, min(100, int(confidence)))


def generate_recommendation(confidence_score: int) -> str:
    if confidence_score >= 80:
        return "You are doing great. Start advanced challenges."
    elif confidence_score >= 60:
        return "Practice intermediate problems regularly."
    elif confidence_score >= 40:
        return "Revise fundamentals and fix detected gaps."
    else:
        return "Strong gaps detected. Follow a guided learning path."
