from fastapi import APIRouter
from pydantic import BaseModel

# ✅ IMPORT THE SERVICE
from backend.services.skill_engine import analyze_skill


router = APIRouter(
    prefix="/analyze",
    tags=["Skill Analysis"]
)


class CodeAnalysisRequest(BaseModel):
    language: str
    code: str
    diagnostics: str | None = None


@router.post("/code")
def analyze_code(request: CodeAnalysisRequest):
    """
    Analyze user-written code and return skill gap insights
    """

    result = analyze_skill(
        language=request.language,
        code=request.code,
        diagnostics=request.diagnostics
    )

    return result
