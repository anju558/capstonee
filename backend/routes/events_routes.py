from fastapi import APIRouter, Depends, Body
from datetime import datetime

from backend.auth import get_current_user
from backend.services.event_processor import process_event
from backend.database import events_collection

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/")
async def ingest_event(
    event: dict = Body(...),
    user=Depends(get_current_user)
):
    """
    Ingest and store a skill-related event.
    """

    # ✅ FIX: use user["sub"] instead of user["_id"]
    event["user_id"] = str(user["sub"])

    processed = await process_event(event)

    record = {
        **processed,
        "user_id": str(user["sub"]),
        "created_at": datetime.utcnow()
    }

    await events_collection.insert_one(record)

    return {
        "status": "stored",
        "skill": processed.get("skill"),
        "gap": processed.get("gap"),
        "event_type": processed.get("event_type")
    }