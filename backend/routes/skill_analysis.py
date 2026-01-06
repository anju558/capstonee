from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

# ✅ IMPORT UNIFIED PIPELINE
from backend.services.ai_pipeline import unified_ai_pipeline


router = APIRouter(
    prefix="/analyze",
    tags=["Skill Analysis"]
)


class CodeAnalysisRequest(BaseModel):
    language: str
    code: str
    diagnostics: Optional[List[str]] = []


@router.post("/code")
async def analyze_code(request: CodeAnalysisRequest):
    """
    Unified AI analysis:
    Code → Skill gaps → Knowledge retrieval → Improvements
    """

    diagnostics_text = (
        "\n".join(request.diagnostics)
        if request.diagnostics
        else None
    )

    result = await unified_ai_pipeline(
        language=request.language,
        code=request.code,
        diagnostics=diagnostics_text  
    )

    return result
