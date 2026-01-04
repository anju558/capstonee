from fastapi import APIRouter, Depends, Body
from datetime import datetime

from backend.auth import get_current_user
from backend.services.event_processor import process_event
from backend.database import events_collection

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/")
async def ingest_event(
    event: dict = Body(..., example={
        "event_type": "compile_error",
        "tool": "VSCode",
        "language": "Python",
        "message": "IndentationError"
    }),
    user=Depends(get_current_user)
):
    # Attach user info
    event["user_id"] = user["_id"]

    # Process event
    processed = await process_event(event)

    # Store event in MongoDB
    record = {
        **processed,
        "user_id": user["_id"],
        "created_at": datetime.utcnow()
    }

    await events_collection.insert_one(record)

    return {
        "status": "stored",
        "data": processed
    }
