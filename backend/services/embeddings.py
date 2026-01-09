from sentence_transformers import SentenceTransformer
import numpy as np

_model = None  # lazy-loaded


def get_model():
    global _model
    if _model is None:
        try:
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            raise RuntimeError(
                "Embedding model could not be loaded. "
                "Check internet access or HuggingFace availability."
            ) from e
    return _model


def embed_text(text: str) -> np.ndarray:
    try:
        model = get_model()
        return model.encode(text)
    except Exception:
        # fallback dummy vector (safe)
        return np.zeros(384)

