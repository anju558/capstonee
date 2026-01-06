import numpy as np
from backend.database import knowledge_collection
from backend.services.embeddings import embed_text


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


async def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    Semantic search using cosine similarity
    """

    query_vec = embed_text(query)

    docs = await knowledge_collection.find().to_list(length=1000)

    scored = []
    for doc in docs:
        score = cosine_similarity(query_vec, doc["embedding"])
        scored.append((score, doc["content"]))

    scored.sort(key=lambda x: x[0], reverse=True)

    top_chunks = [text for _, text in scored[:top_k]]

    return "\n\n".join(top_chunks)
