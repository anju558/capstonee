from backend.database import skills_collection

NORMALIZE = {
    "py": "python",
    "js": "javascript",
    "mongo": "mongodb"
}

def normalize(skill: str) -> str:
    return NORMALIZE.get(skill.lower(), skill.lower())

async def get_or_create_skill(skill_name: str):
    skill_name = normalize(skill_name)

    skill = await skills_collection.find_one({"skill_name": skill_name})
    if skill:
        return skill

    new_skill = {
        "skill_name": skill_name,
        "category": "auto-discovered",
        "verified": False
    }

    await skills_collection.insert_one(new_skill)
    return new_skill
