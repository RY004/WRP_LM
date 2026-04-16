"""Deterministic ONNX-shaped embedding backend.

The production dependency boundary is ONNX/BGE-M3, but CI should not download
large model artifacts. This backend gives stable dense vectors with the same
service contract so ranking, storage, and fallback behavior are exercised.
"""

import hashlib
import math

from saturn.embeddings.backends.base import EmbeddingVector


class OnnxEmbeddingBackend:
    model_name = "bge-m3-onnx-local"
    dimensions = 64

    def embed(self, texts: list[str]) -> list[EmbeddingVector]:
        return [
            EmbeddingVector(
                values=_normalize(_hashing_vector(text, self.dimensions)),
                model_name=self.model_name,
                dimensions=self.dimensions,
            )
            for text in texts
        ]


def _hashing_vector(text: str, dimensions: int) -> list[float]:
    vector = [0.0] * dimensions
    tokens = [token.lower() for token in text.split() if token.strip()]
    for token in tokens or [text]:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    return vector


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]
