from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from backend.auth import get_current_user
from backend.services.ai_pipeline import unified_ai_pipeline
from backend.services.event_processor import process_event
from backend.database import events_collection

router = APIRouter(
    prefix="/analyze",
    tags=["Skill Analysis"]
)


# -------------------------------------------------
# 📥 Request Model
# -------------------------------------------------
class CodeAnalysisRequest(BaseModel):
    language: str
    code: str
    diagnostics: Optional[List[str]] = []


# -------------------------------------------------
# 🧠 Code Analysis Endpoint
# -------------------------------------------------
@router.post("/code")
async def analyze_code(
    request: CodeAnalysisRequest,
    user=Depends(get_current_user)
):
    """
    Flow:
    Code → AI Analysis → Skill State Update → RAG → Event Storage
    """

    # Convert diagnostics list to text
    diagnostics_text = (
        "\n".join(request.diagnostics)
        if request.diagnostics
        else None
    )

    # -------------------------------------------------
    # 1️⃣ Run unified AI pipeline (IMPORTANT: pass user_id)
    # -------------------------------------------------
    ai_result = await unified_ai_pipeline(
        language=request.language,
        code=request.code,
        diagnostics=diagnostics_text,
        user_id=str(user["_id"])   # ✅ REQUIRED for skill memory
    )

    # -------------------------------------------------
    # 2️⃣ Create analytics / event record
    # -------------------------------------------------
    event = {
        "user_id": str(user["_id"]),   # ✅ always string
        "language": request.language,
        "event_type": "code_analysis",
        "skill_gaps": ai_result["analysis"].get("skill_gaps", []),
        "confidence_score": ai_result["analysis"].get("confidence_score", 0),
        "created_at": datetime.utcnow()
    }

    # Optional processing (normalization / tagging)
    processed_event = await process_event(event)

    # -------------------------------------------------
    # 3️⃣ Store event in MongoDB
    # -------------------------------------------------
    await events_collection.insert_one(processed_event)

    # -------------------------------------------------
    # 4️⃣ Return AI response to client
    # -------------------------------------------------
    return {
        "status": "success",
        "analysis": ai_result["analysis"],
        "learning_context": ai_result["learning_context"],
        "final_guidance": ai_result["final_guidance"]
    }
