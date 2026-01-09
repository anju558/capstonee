import re

CANONICAL_SKILLS = {
    "syntax": ["syntax", "indentation", "compile", "error"],
    "loops": ["loop", "iteration", "for", "while"],
    "functions": ["function", "encapsulation", "def"],
    "variables": ["variable", "naming", "identifier"],
    "readability": ["readability", "clean", "robust"],
}

def normalize_gap_to_skill(text: str) -> str | None:
    text = text.lower()

    for skill, keywords in CANONICAL_SKILLS.items():
        if any(k in text for k in keywords):
            return skill

    return None
