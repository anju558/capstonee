def generate_recommendation(skill: str, gap: float):
    if gap >= 50:
        severity = "critical"
        action = f"Immediate advanced training required for {skill}"
    elif gap >= 30:
        severity = "high"
        action = f"Assign intermediate projects for {skill}"
    elif gap >= 15:
        severity = "medium"
        action = f"Recommend practice exercises for {skill}"
    else:
        severity = "low"
        action = f"{skill} proficiency is stable"

    return {
        "skill": skill,
        "gap": gap,
        "severity": severity,
        "action": action
    }
