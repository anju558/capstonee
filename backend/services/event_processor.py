async def process_event(event: dict) -> dict:
    language = event.get("language", "unknown")

    difficulty = 3
    if event["event_type"] in ["compile_error", "runtime_error"]:
        difficulty = 4

    gap_detected = event["event_type"] in ["compile_error", "runtime_error"]

    return {
        "features": {
            "skill": language.lower(),
            "difficulty": difficulty
        },
        "gap_analysis": {
            "gap": gap_detected,
            "reason": event.get("message", "")
        }
    }
