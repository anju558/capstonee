def build_features(event: dict):
    """
    Convert raw event into ML-safe features
    """

    return {
        "skill": event.get("skill", "unknown"),
        "action": event.get("action", "unknown"),
        "difficulty": event.get("difficulty", 0),
        "timestamp": event.get("timestamp")
    }
