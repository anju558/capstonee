from backend.services.retrieval import retrieve_context
from backend.services.llm_engine import generate_answer


async def rag_answer(question: str) -> str:
    """
    Full RAG pipeline
    """

    context = await retrieve_context(question)

    if not context:
        return "No relevant knowledge found."

    answer = generate_answer(
        question=question,
        context=context
    )

    return answer
