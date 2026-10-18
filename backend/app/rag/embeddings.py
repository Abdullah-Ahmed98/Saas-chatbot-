from functools import lru_cache

import numpy as np

from app.models.knowledge import EMBED_DIM


@lru_cache(maxsize=1)
def get_embedder():
    """Lazily load the local embedding model (runs once, ~90MB download first time)."""
    from sentence_transformers import SentenceTransformer

    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    return SentenceTransformer(model_name, device="cpu")


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts into 384-d vectors on CPU."""
    model = get_embedder()
    vecs = model.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
    return [list(map(float, v)) for v in vecs]


def embed_query(query: str) -> list[float]:
    return embed([query])[0]


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
