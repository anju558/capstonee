from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from collections import defaultdict
from datetime import datetime

from backend.auth import get_current_user, require_admin
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
# 👑 ADMIN: GET ALL USERS (FOR ADMIN DASHBOARD)
# -------------------------------------------------
@router.get("/admin/users")
async def get_all_users(admin=Depends(require_admin)):

    users = await users_collection.find().to_list(1000)

    clean_users = []

    for u in users:
        clean_users.append({
            "id": str(u["_id"]),
            "username": u.get("username"),
            "email": u.get("email"),
            "role": u.get("role"),
            "created_at": u.get("created_at")
        })

    return clean_users


# -------------------------------------------------
# 👑 ADMIN: VIEW ANY USER REPORT
# -------------------------------------------------
@router.get("/admin/{user_id}")
async def get_user_skill_report(
    user_id: str,
    admin=Depends(require_admin)
):
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    target = await users_collection.find_one({"_id": obj_id})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    return await generate_skill_report(str(obj_id))


# -------------------------------------------------
# 📈 USER: SKILL HISTORY (DAILY CLEAN TREND)
# -------------------------------------------------
@router.get("/skills/history")
async def get_skill_history(user=Depends(get_current_user)):

    history = await skill_history_collection.find(
        {"user_id": user["sub"]}
    ).to_list(1000)

    if not history:
        return []

    grouped = defaultdict(list)

    for h in history:
        if h.get("created_at"):
            date_key = h["created_at"].date()
            grouped[date_key].append(
                float(h.get("confidence_score", 0))
            )

    clean_history = []

    for date, scores in sorted(grouped.items()):
        average_score = sum(scores) / len(scores)

        clean_history.append({
            "created_at": datetime.combine(
                date,
                datetime.min.time()
            ),
            "confidence_score": round(average_score, 2)
        })

    return clean_history


# -------------------------------------------------
# 👑 ADMIN: USER HISTORY (DAILY CLEAN)
# -------------------------------------------------
@router.get("/admin/{user_id}/history")
async def get_user_history(
    user_id: str,
    admin=Depends(require_admin)
):

    try:
        ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    history = await skill_history_collection.find(
        {"user_id": user_id}
    ).to_list(1000)

    if not history:
        return []

    grouped = defaultdict(list)

    for h in history:
        if h.get("created_at"):
            date_key = h["created_at"].date()
            grouped[date_key].append(
                float(h.get("confidence_score", 0))
            )

    clean_history = []

    for date, scores in sorted(grouped.items()):
        average_score = sum(scores) / len(scores)

        clean_history.append({
            "created_at": datetime.combine(
                date,
                datetime.min.time()
            ),
            "confidence_score": round(average_score, 2)
        })

    return clean_history