def detect_gap(observed: dict, expected: dict | None = None):
    """
    Compare observed skill level with expected skill level.
    If expected is not provided, assume no gap.
    """

    if not expected:
        return {
            "gap": False,
            "reason": "No expected skill baseline provided"
        }

    observed_level = observed.get("level", 0)
    expected_level = expected.get("level", 0)

    return {
        "gap": observed_level < expected_level,
        "observed_level": observed_level,
        "expected_level": expected_level
    }
