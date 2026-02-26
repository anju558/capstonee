from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from backend.auth import get_current_user
from backend.services.skill_summary import generate_skill_report
from backend.database import users_collection, skill_history_collection

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# -------------------------------------------------
# 👤 USER: CURRENT SKILL REPORT
# -------------------------------------------------
@router.get("/skills")
async def get_skill_report(user=Depends(get_current_user)):
    return await generate_skill_report(user["sub"])


# -------------------------------------------------
# 👑 ADMIN: VIEW ANY USER REPORT
# -------------------------------------------------
@router.get("/admin/{user_id}")
async def get_user_skill_report(user_id: str, user=Depends(get_current_user)):

    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    target = await users_collection.find_one({"_id": obj_id})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    return await generate_skill_report(str(obj_id))


# -------------------------------------------------
# 🔧 SAFE CONVERTER (ObjectId → string)
# -------------------------------------------------
def convert_objectids(data):
    if isinstance(data, list):
        return [convert_objectids(item) for item in data]
    elif isinstance(data, dict):
        return {k: convert_objectids(v) for k, v in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data


# -------------------------------------------------
# 📈 USER: SKILL HISTORY (CLEAN FOR GRAPH)
# -------------------------------------------------
@router.get("/skills/history")
async def get_skill_history(user=Depends(get_current_user)):

    history = await skill_history_collection.find(
        {"user_id": user["sub"]}
    ).sort("created_at", 1).to_list(500)

    clean_history = []

    for h in history:
        clean_history.append({
            "confidence_score": h.get("confidence_score", 0),
            "created_at": h.get("created_at")
        })

    return clean_history


# -------------------------------------------------
# 👑 ADMIN: USER HISTORY (CLEAN)
# -------------------------------------------------
@router.get("/admin/{user_id}/history")
async def get_user_history(user_id: str, user=Depends(get_current_user)):

    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    history = await skill_history_collection.find(
        {"user_id": user_id}
    ).sort("created_at", 1).to_list(500)

    clean_history = []

    for h in history:
        clean_history.append({
            "confidence_score": h.get("confidence_score", 0),
            "created_at": h.get("created_at")
        })

    return clean_history