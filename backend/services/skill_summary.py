from collections import defaultdict
from backend.database import events_collection


def calculate_confidence(events):

    total = len(events)
    if total == 0:
        return 50.0

    successes = sum(1 for e in events if not e.get("gap"))
    accuracy = successes / total

    avg_difficulty = sum(e.get("difficulty", 1) for e in events) / total
    difficulty_factor = min(1, avg_difficulty / 5)

    score = (0.7 * accuracy) + (0.3 * difficulty_factor)

    return round(score * 100, 2)


async def generate_skill_report(user_id: str):

    events = await events_collection.find(
        {"user_id": user_id}
    ).sort("created_at", 1).to_list(1000)

    skills_data = defaultdict(list)

    for e in events:
        skill = e.get("language") or e.get("skill")
        if skill:
            skills_data[skill.lower()].append(e)

    report = []

    for skill, skill_events in skills_data.items():

        confidence_score = calculate_confidence(skill_events)

        report.append({
            "skill": skill,
            "confidence_score": confidence_score
        })

    overall = (
        round(sum(r["confidence_score"] for r in report) / len(report), 2)
        if report else 50.0
    )

    return {
        "overall_score": overall,
        "skills": report
    }