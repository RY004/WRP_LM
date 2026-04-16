"""OpenVINO embedding backend boundary."""

from saturn.embeddings.backends.onnx import OnnxEmbeddingBackend


class OpenVinoEmbeddingBackend(OnnxEmbeddingBackend):
    model_name = "bge-m3-openvino-local"
