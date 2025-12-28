from fastapi import APIRouter, Depends
from backend.auth import require_role
from backend.services.analytics import skill_gap_summary

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics 🔒"]
)

@router.get("/skill-gaps")
async def get_skill_gaps(
    admin=Depends(require_role("admin"))
):
    return {
        "status": "success",
        "data": await skill_gap_summary()
    }
