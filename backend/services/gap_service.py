def detect_gap(observed: int, expected: int) -> int:
    """
    Returns numeric gap value
    """
    return max(expected - observed, 0)
