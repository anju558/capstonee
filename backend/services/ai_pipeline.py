from backend.services.skill_engine import analyze_skill
from backend.services.retrieval import retrieve_context
from backend.services.llm_engine import generate_answer
from backend.services.skill_state_service import upsert_skill_state
from backend.services.taxonomy_service import normalize
from backend.services.skill_normalizer import normalize_gap_to_skill

async def unified_ai_pipeline(
    language: str,
    code: str,
    diagnostics: str | None = None,
    user_id: str | None = None
):
    """
    Full AI pipeline:
    Code → Skill Analysis → Skill State → RAG → Final Answer
    """

    # 1️⃣ Analyze code with LLM
    skill_result = analyze_skill(
        language=language,
        code=code,
        diagnostics=diagnostics
    )

    skill_gaps = skill_result.get("skill_gaps", [])
    confidence = float(skill_result.get("confidence_score", 0))
    estimated_level = int(skill_result.get("estimated_level", 2))

    # 2️⃣ Persist PRIMARY skill (language)
    if user_id:
        await upsert_skill_state(
            user_id=str(user_id),
            skill=normalize(language),
            estimated_level=estimated_level,
            confidence_score=confidence
        )
        for gap in skill_gaps:
            normalized = normalize_gap_to_skill(gap)
            if not normalized:
                continue  # ignore junk
            await upsert_skill_state(
                user_id=user_id,
                skill=normalized,
                estimated_level=max(1, estimated_level - 1),
                confidence_score=confidence * 0.8
            )

    # 4️⃣ Build RAG query
    if skill_gaps:
        query = f"Explain and improve: {', '.join(skill_gaps)}"
    else:
        query = f"Improve and optimize this {language} code"

    # 5️⃣ Retrieve knowledge
    context_chunks = await retrieve_context(query, top_k=5)
    context = "\n".join(context_chunks)

    # 6️⃣ Generate final answer
    final_answer = generate_answer(
        question=query,
        context=context
    )

    return {
        "analysis": skill_result,
        "learning_context": context_chunks,
        "final_guidance": final_answer
    }
