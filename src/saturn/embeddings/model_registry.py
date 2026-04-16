"""Embedding model registry."""

from saturn.embeddings.backends.base import EmbeddingBackend
from saturn.embeddings.backends.onnx import OnnxEmbeddingBackend
from saturn.embeddings.backends.openvino import OpenVinoEmbeddingBackend


class EmbeddingModelRegistry:
    def __init__(self, backends: dict[str, EmbeddingBackend] | None = None) -> None:
        self.backends = backends or {
            "onnx": OnnxEmbeddingBackend(),
            "openvino": OpenVinoEmbeddingBackend(),
        }

    def get(self, name: str = "onnx") -> EmbeddingBackend:
        try:
            return self.backends[name]
        except KeyError as exc:
            raise ValueError(f"Unsupported embedding backend: {name}") from exc


def default_embedding_backend() -> EmbeddingBackend:
    return EmbeddingModelRegistry().get("onnx")
