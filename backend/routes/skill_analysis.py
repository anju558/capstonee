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

    # 1️⃣ Run AI analysis FIRST
    result = analyze_skill(
        language=request.language,
        code=request.code,
        combined_context=request.diagnostics or ""
    )

    # 2️⃣ Now generate updated skill report (after event is saved)
    report = await generate_skill_report(user["sub"])
    overall_score = report.get("overall_score", 50)

    # 3️⃣ Save updated overall score into history
    await skill_history_collection.insert_one({
        "user_id": user["sub"],
        "confidence_score": overall_score,
        "created_at": datetime.utcnow()
    })

    return {
        "analysis": result
    }