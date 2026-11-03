"""Embedding Engine — Local semantic similarity computations with synonym awareness."""

import logging
import math
import re

logger = logging.getLogger(__name__)

# Common Tech Synonyms & Concept Equivalences for high-fidelity matching
SYNONYM_MAP = {
    "k8s": "kubernetes",
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "gcp": "google cloud",
    "aws": "amazon web services",
    "rest": "rest api",
    "restful": "rest api",
    "fastapi": "python api",
    "reactjs": "react",
    "nodejs": "node.js",
    "ci/cd": "continuous integration",
    "ml": "machine learning",
    "dl": "deep learning",
    "llm": "large language models",
    "nlp": "natural language processing",
}


class EmbeddingEngine:
    """Manages semantic similarity computations between candidate evidence and requirements."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._attempted_load = False

    def _get_model(self):
        """Lazy loader for sentence-transformers only if explicitly enabled or locally cached."""
        import os
        if os.environ.get("LOAD_HEAVY_TRANSFORMERS") != "1":
            return None

        if not self._attempted_load:
            self._attempted_load = True
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name, local_files_only=True)
                logger.info("Loaded cached SentenceTransformer: %s", self.model_name)
            except Exception:
                self._model = None
        return self._model

    def compute_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate cosine semantic similarity between two textual fragments."""
        if not text_a or not text_b:
            return 0.0

        str_a = text_a.strip().lower()
        str_b = text_b.strip().lower()

        # Exact or substring match shortcut
        if str_a == str_b or str_a in str_b or str_b in str_a:
            return 1.0

        # Try Sentence Transformer first if available
        model = self._get_model()
        if model is not None:
            try:
                embeddings = model.encode([text_a, text_b])
                import numpy as np
                norm_a = np.linalg.norm(embeddings[0])
                norm_b = np.linalg.norm(embeddings[1])
                if norm_a > 0 and norm_b > 0:
                    sim = float(np.dot(embeddings[0], embeddings[1]) / (norm_a * norm_b))
                    return max(0.0, min(1.0, sim))
            except Exception as e:
                logger.warning("SentenceTransformer encoding failed: %s", e)

        # High-performance NLP Fallback: Token Jaccard + Character N-Gram + Synonym Graph
        return self._token_semantic_similarity(str_a, str_b)

    def _normalize_tokens(self, text: str) -> set[str]:
        """Normalize text and expand domain synonyms."""
        tokens = set(re.findall(r"\b[a-zA-Z0-9+#.-]+\b", text))
        expanded = set(tokens)
        for t in tokens:
            if t in SYNONYM_MAP:
                expanded.add(SYNONYM_MAP[t])
        return expanded

    def _token_semantic_similarity(self, a: str, b: str) -> float:
        """Compute robust set similarity with character tri-grams."""
        set_a = self._normalize_tokens(a)
        set_b = self._normalize_tokens(b)

        if not set_a or not set_b:
            return 0.0

        # Token intersection
        intersection = set_a.intersection(set_b)
        union = set_a.union(set_b)
        jaccard = len(intersection) / len(union) if union else 0.0

        # Sub-token overlap (e.g. "Kubernetes cluster" vs "Kubernetes")
        contained_count = sum(1 for tok in set_a if any(tok in other for other in set_b))
        containment = contained_count / max(len(set_a), len(set_b))

        # Tri-gram character similarity
        ngrams_a = set(a[i:i+3] for i in range(len(a) - 2))
        ngrams_b = set(b[i:i+3] for i in range(len(b) - 2))
        ngram_sim = len(ngrams_a & ngrams_b) / len(ngrams_a | ngrams_b) if (ngrams_a | ngrams_b) else 0.0

        score = (jaccard * 0.5) + (containment * 0.3) + (ngram_sim * 0.2)
        return max(0.0, min(1.0, score))
