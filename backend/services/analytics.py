from backend.database import events_collection

async def skill_gap_summary():
    pipeline = [
        {
            "$group": {
                "_id": "$skill",
                "avg_gap": {"$avg": "$gap"},
                "max_gap": {"$max": "$gap"},
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
