"""Embedding batching helpers."""


def batch_texts(items: list[str], batch_size: int = 32) -> list[list[str]]:
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    return [items[index : index + batch_size] for index in range(0, len(items), batch_size)]
