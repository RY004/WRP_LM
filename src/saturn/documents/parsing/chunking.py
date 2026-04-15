"""Chunk parsed sections into retrieval-ready text rows."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class ParsedChunk:
    section_ordinal: int | None
    text: str
    heading_path_text: str
    heading_path_ltree: str
    metadata: dict = field(default_factory=dict)

    @property
    def token_count_estimate(self) -> int:
        return max(1, len(self.text.split()))


def chunk_section_text(
    text: str,
    heading_text: str,
    heading_ltree: str,
    section_ordinal: int | None,
    max_chars: int = 1200,
) -> list[ParsedChunk]:
    clean = text.strip()
    if not clean:
        return []
    chunks: list[ParsedChunk] = []
    start = 0
    while start < len(clean):
        end = min(len(clean), start + max_chars)
        if end < len(clean):
            split_at = clean.rfind("\n", start, end)
            if split_at <= start:
                split_at = clean.rfind(" ", start, end)
            if split_at > start:
                end = split_at
        chunk_text = clean[start:end].strip()
        if chunk_text:
            chunks.append(
                ParsedChunk(
                    section_ordinal=section_ordinal,
                    text=chunk_text,
                    heading_path_text=heading_text,
                    heading_path_ltree=heading_ltree,
                )
            )
        start = end + 1
    return chunks
