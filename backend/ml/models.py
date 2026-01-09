def predict_mastery(confidence_score: float) -> str:
    """
    Predict mastery level from final confidence score (0–100).
    """

    if confidence_score >= 80:
        return "high"
    elif confidence_score >= 50:
        return "medium"
    else:
        return "low"
