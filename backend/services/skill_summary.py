from backend.database import events_collection
from backend.services.skill_insights import (
    compute_confidence,
    generate_recommendation
)

async def generate_skill_report(user_id):
    summary = {}

    cursor = events_collection.aggregate([
        {
            "$match": {
                "user_id": user_id,
                "language": {"$ne": None}
            }
        },
        {
            "$group": {
                "_id": "$language",
                "attempts": {"$sum": 1},
                "avg_difficulty": {"$avg": "$difficulty"},
                "gaps_detected": {"$sum": "$gap"}
            }
        }
    ])

    async for doc in cursor:
        language = doc["_id"]

        if not language:
            continue  # safety guard

        confidence = compute_confidence(doc)

        summary[language.lower()] = {
            "attempts": doc.get("attempts", 0),
            "avg_difficulty": round(doc.get("avg_difficulty", 0), 2),
            "gaps_detected": doc.get("gaps_detected", 0),
            "confidence_score": confidence,
            "recommendation": generate_recommendation(confidence)
        }

    return summary
