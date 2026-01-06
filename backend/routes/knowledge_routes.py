from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.knowledge_ingest import ingest_knowledge

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


class KnowledgeIngestRequest(BaseModel):
    skill: str
    content: str


@router.post("/ingest")
async def ingest_knowledge_api(data: KnowledgeIngestRequest):
    result = await ingest_knowledge(
        skill=data.skill,
        content=data.content
    )

    return {
        "message": "Knowledge ingested successfully",
        "details": result
    }
