from datetime import datetime
from backend.database import user_skills_collection


async def process_event(event: dict) -> dict:
    """
    Normalize and store skill-related events.
    This feeds analytics & confidence scoring.
    """

    language = event.get("language", "unknown").lower()

    # ✅ FIX: gap comes from skill_gaps list
    gap_detected = bool(event.get("skill_gaps"))

    difficulty = 4 if gap_detected else 2

    doc = {
        "user_id": str(event["user_id"]),   # ✅ always string
        "skill": language,
        "event_type": event.get("event_type", "unknown"),
        "difficulty": difficulty,
        "gap": gap_detected,
        "reason": event.get("message", ""),
        "created_at": datetime.utcnow()
    }

    await user_skills_collection.insert_one(doc)

    return doc
