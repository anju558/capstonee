from fastapi import APIRouter, Depends
from backend.auth import get_current_user
from backend.services.event_processor import process_event

router = APIRouter(
    prefix="/api/events",
    tags=["Events 🔒"]
)

@router.post("/")
async def ingest_event(
    event: dict,
    user=Depends(get_current_user)
):
    event["user_id"] = user.get("sub")

    result = await process_event(event)

    return {
        "status": "processed",
        "result": result
    }
