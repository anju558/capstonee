from fastapi import APIRouter, Depends
from backend.services.event_processor import process_event
from backend.auth import get_current_user

router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("/code")
async def analyze_code(payload: dict, user=Depends(get_current_user)):
    """
    Receives code from VS Code extension
    """
    event = {
        "user_id": str(user["_id"]),
        "skill": payload.get("skill", "general"),
        "code": payload.get("code"),
        "language": payload.get("language", "python"),
        "event_type": "code_analysis"
    }

    result = await process_event(event)

    return {
        "skill": payload.get("skill", "general"),
        "score": result.get("gap", {}).get("score", 0),
        "issue": result.get("gap", {}).get("issue"),
        "recommendation": result.get("recommendation")
    }
