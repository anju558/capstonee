from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.auth import get_current_user
from backend.services.rag_engine import rag_answer

router = APIRouter(prefix="/rag", tags=["RAG"])


# -------------------------------------------------
# 📥 Request Model
# -------------------------------------------------
class RagRequest(BaseModel):
    question: str


# -------------------------------------------------
# 🧠 RAG Endpoint
# -------------------------------------------------
@router.post("/ask")
async def ask_rag(
    data: RagRequest,
    user=Depends(get_current_user)
):
    """
    RAG-based question answering.
    Used by frontend / browser extension.
    """

    enriched_question = f"{data.question}. User role: {user['role']}"

    answer = await rag_answer(enriched_question)

    return {
        "answer": answer
    }
