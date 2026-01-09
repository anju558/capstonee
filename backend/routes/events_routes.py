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
    This endpoint does NOT return MongoDB documents.
    """

    # Always enforce user_id as string
    event["user_id"] = str(user["_id"])

    # Normalize & process event
    processed = await process_event(event)

    # Store full record separately (DB only)
    record = {
        **processed,
        "user_id": str(user["_id"]),
        "created_at": datetime.utcnow()
    }

    await events_collection.insert_one(record)

    # ✅ SAFE RESPONSE (NO ObjectId)
    return {
        "status": "stored",
        "skill": processed.get("skill"),
        "gap": processed.get("gap"),
        "event_type": processed.get("event_type")
    }
