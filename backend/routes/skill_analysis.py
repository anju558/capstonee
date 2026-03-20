# skill_analysis.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime

from backend.auth import get_current_user
from backend.services.skill_engine import analyze_skill
from backend.services.skill_summary import generate_skill_report
from backend.database import skill_history_collection

router = APIRouter(prefix="/analyze", tags=["Analysis"])


class CodeRequest(BaseModel):
    language: str
    code: str
    diagnostics: str | None = None


@router.post("/code")
async def analyze_code(request: CodeRequest, user=Depends(get_current_user)):

    # 1️⃣ Run AI analysis
    result = analyze_skill(
        language=request.language,
        code=request.code,
        combined_context=request.diagnostics or ""
    )

    # 2️⃣ Get updated overall score
    report = await generate_skill_report(user["sub"])
    overall_score = float(report.get("overall_score", 50))

    now = datetime.utcnow()

    # 🔧 FIX: use datetime instead of date
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 3️⃣ Check if today's record exists
    existing = await skill_history_collection.find_one({
        "user_id": user["sub"],
        "date": today
    })

    if existing:
        # Update today's score
        await skill_history_collection.update_one(
            {"_id": existing["_id"]},
            {
                "$set": {
                    "confidence_score": overall_score,
                    "updated_at": now
                }
            }
        )
    else:
        # Insert new daily record
        await skill_history_collection.insert_one({
            "user_id": user["sub"],
            "confidence_score": overall_score,
            "date": today,
            "created_at": now
        })

    return {
        "analysis": result
    }