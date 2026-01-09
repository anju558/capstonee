from datetime import datetime
from typing import List, Dict

from backend.database import user_skill_state_collection


async def upsert_skill_state(
    user_id: str,
    skill: str,
    estimated_level: int,
    confidence_score: float
):
    """
    Insert or update a user's skill state.
    - One document per (user_id, skill)
    - Updates level & confidence over time
    """

    await user_skill_state_collection.update_one(
        {"user_id": user_id, "skill": skill},
        {
            "$set": {
                "current_level": estimated_level,
                "confidence_score": confidence_score,
                "last_evaluated": datetime.utcnow()
            },
            "$setOnInsert": {
                "target_level": 5
            }
        },
        upsert=True
    )


async def get_user_skill_states(user_id: str) -> List[Dict]:
    """
    Fetch all skill states for a user
    """
    cursor = user_skill_state_collection.find(
        {"user_id": user_id},
        {"_id": 0}
    )

    return [doc async for doc in cursor]


def compute_skill_gap(skill_state: Dict) -> Dict:
    """
    Compute gap & priority for a skill
    """
    current = skill_state["current_level"]
    target = skill_state["target_level"]

    gap = target - current

    if gap >= 3:
        priority = "HIGH"
    elif gap == 2:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return {
        **skill_state,
        "gap": gap,
        "priority": priority
    }
