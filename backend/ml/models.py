def predict_mastery(features: dict):
    if features["normalized_gap"] > 0.6:
        return "low"
    elif features["normalized_gap"] > 0.3:
        return "medium"
    return "high"
