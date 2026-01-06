from datetime import datetime
from typing import List
from backend.database import knowledge_collection
from backend.services.embeddings import embed_text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


async def ingest_knowledge(skill: str, content: str, source: str = "manual"):
    """
    Store knowledge chunks with embeddings
    """

    chunks = chunk_text(content)
    documents = []

    for idx, chunk in enumerate(chunks):
        embedding = embed_text(chunk)

        documents.append({
            "skill": skill,
            "content": chunk,
            "embedding": embedding.tolist(),
            "source": source,
            "chunk_index": idx,
            "created_at": datetime.utcnow()
        })

    if documents:
        await knowledge_collection.insert_many(documents)

    return {
        "skill": skill,
        "chunks_added": len(documents)
    }
