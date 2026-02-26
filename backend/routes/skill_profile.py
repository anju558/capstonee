from fastapi import APIRouter, Depends
from backend.auth import get_current_user
from backend.services.skill_fusion_service import get_merged_skill_profile
from backend.services.skill_summary import generate_skill_report

router = APIRouter(prefix="/skills", tags=["Skills"])



@router.get("/profile")
async def skill_profile(user=Depends(get_current_user)):
    return await generate_skill_report(user["_id"])

