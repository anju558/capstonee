from backend.services.skill_engine import analyze_skill
from backend.services.retrieval import retrieve_context
from backend.services.llm_engine import generate_answer


async def unified_ai_pipeline(
    language: str,
    code: str,
    diagnostics: str | None = None
):
    """
    Full AI pipeline:
    Code → Skill Analysis → RAG → Final LLM Answer
    """

    # 1️⃣ Analyze code skills
    skill_result = analyze_skill(
        language=language,
        code=code,
        diagnostics=diagnostics
    )

    skill_gaps = skill_result.get("skill_gaps", [])

    # 2️⃣ Build retrieval query
    if skill_gaps:
        query = f"Explain and improve the following concepts: {', '.join(skill_gaps)}"
    else:
        query = f"Improve and optimize this {language} code"

    # 3️⃣ Retrieve knowledge (RAG)
    context_chunks = await retrieve_context(query, top_k=5)
    context = "\n".join(context_chunks)

    # 4️⃣ Generate final response
    final_answer = generate_answer(
        question=query,
        context=context
    )

    # 5️⃣ Unified structured response
    return {
        "analysis": skill_result,
        "learning_context": context_chunks,
        "final_guidance": final_answer
    }
