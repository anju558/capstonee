from backend.database import events_collection


async def skill_gap_summary():
    """
    Aggregated view of skill gaps across all events.
    Used for analytics / dashboards (NOT coaching).
    """

    pipeline = [
        {
            "$match": {
                "skill": {"$ne": None}
            }
        },
        {
            "$group": {
                "_id": "$skill",
                "avg_gap": {"$avg": {"$cond": ["$gap", 1, 0]}},
                "max_gap": {"$max": {"$cond": ["$gap", 1, 0]}},
                "count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "skill": "$_id",
                "avg_gap": {"$round": ["$avg_gap", 2]},
                "max_gap": 1,
                "events": "$count",
                "_id": 0
            }
        },
        {"$sort": {"avg_gap": -1}}
    ]

    results = []
    async for row in events_collection.aggregate(pipeline):
        results.append(row)

    return results
