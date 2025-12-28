def build_features(event: dict):
    expected = event.get("expected", 1)
    actual = event.get("actual", 0)

    gap = expected - actual

    return {
        "skill": event["skill"],
        "gap": gap,
        "normalized_gap": gap / max(expected, 1),
        "attempts": event.get("attempts", 1),
        "time_spent": event.get("time_spent", 0),
        "difficulty": event.get("difficulty", 1),
    }
