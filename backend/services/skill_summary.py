from backend.database import user_skills_collection
from backend.services.skill_insights import (
    compute_confidence,
    generate_recommendation
)

async def generate_skill_report(user_id):
    summary = {}

    cursor = user_skills_collection.aggregate([
        {
            "$match": {
                "user_id": str(user_id),
                "skill": {"$ne": None}
            }
        },
        {
            "$group": {
                "_id": "$skill",
                "attempts": {"$sum": 1},
                "avg_difficulty": {"$avg": "$difficulty"},
                "gaps_detected": {
                    "$sum": {
                        "$cond": [{"$eq": ["$gap", True]}, 1, 0]
                    }
                }
            }
        }
    ])

    async for doc in cursor:
        skill = doc["_id"]

        if not skill:
            continue

        confidence = compute_confidence(doc)

        summary[skill.lower()] = {
            "attempts": doc.get("attempts", 0),
            "avg_difficulty": round(doc.get("avg_difficulty", 0), 2),
            "gaps_detected": doc.get("gaps_detected", 0),
            "confidence_score": confidence,
            "recommendation": generate_recommendation(confidence)
        }

    return summary
