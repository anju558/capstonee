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
    # 1️⃣ Analyze code
    raw_result = analyze_skill(code, language, diagnostics)

    if not isinstance(raw_result, dict):
        print("⚠️ analyze_skill returned non-dict:", raw_result)
        raw_result = {}

    confidence_score = float(raw_result.get("confidence_score", 0))
    skill_gaps = raw_result.get("skill_gaps", [])
    estimated_level = int(raw_result.get("estimated_level", 2))

    analysis = {
        "confidence_score": confidence_score,
        "skill_gaps": skill_gaps,
        "simple_explanation": raw_result.get("simple_explanation", ""),
        "corrected_code": raw_result.get("corrected_code", ""),
        "next_steps": raw_result.get("next_steps", [])
    }


    # 2️⃣ Persist skill state
    if user_id:
        await upsert_skill_state(
            user_id=user_id,
            skill=normalize(language),
            estimated_level=estimated_level,
            confidence_score=confidence_score
        )

        for gap in skill_gaps:
            normalized = normalize_gap_to_skill(gap)
            if not normalized:
                continue

            await upsert_skill_state(
                user_id=user_id,
                skill=normalized,
                estimated_level=max(1, estimated_level - 1),
                confidence_score=confidence_score * 0.8
            )

    # 3️⃣ Build RAG query
    query = (
        f"Explain and improve: {', '.join(skill_gaps)}"
        if skill_gaps
        else f"Improve and optimize this {language} code"
    )

    # 4️⃣ Retrieve knowledge
    context_chunks = await retrieve_context(query, top_k=5)

    # 5️⃣ Generate final guidance
    final_answer = generate_answer(
        question=query,
        context="\n".join(context_chunks)
    )

    if isinstance(final_answer, str):
        final_answer = [final_answer]

    if final_answer is None:
        final_answer = []

    final_answer = [a.strip() for a in final_answer if a.strip()]

    return {
        "analysis": analysis,
        "learning_context": context_chunks or [],
        "final_guidance": final_answer
    }
