from fastapi import APIRouter, Depends
from backend.auth import get_current_user
from backend.services.rag_engine import rag_answer

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ask")
async def ask(question: str, user=Depends(get_current_user)):
    enriched_question = f"{question}. User role: {user['role']}"

    answer = await rag_answer(enriched_question)

    return {"answer": answer}
