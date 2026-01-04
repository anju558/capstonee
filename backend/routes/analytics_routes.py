from fastapi import APIRouter, Depends
from backend.auth import get_current_user
from backend.services.skill_summary import generate_skill_report

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/skills")
async def get_skill_report(user=Depends(get_current_user)):
    return await generate_skill_report(user["_id"])
