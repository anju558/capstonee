def build_features(event: dict) -> dict:
    """
    Convert raw event into ML-safe numerical features.

    This function MUST:
    - Be pure (no DB access)
    - Never raise KeyError
    - Match actual event schema used in backend
    """

    return {
        # Core identifiers
        "skill": event.get("skill", "unknown"),
        "event_type": event.get("event_type", "unknown"),

        # Numerical features
        "difficulty": float(event.get("difficulty", 0)),
        "gap": int(event.get("gap", False)),  # boolean → 0/1

        # Time feature (kept raw for now)
        "timestamp": event.get("created_at")
    }
