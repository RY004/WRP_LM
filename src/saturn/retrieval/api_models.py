"""API models for retrieval."""

from pydantic import BaseModel, Field


class RetrievalQuery(BaseModel):
    project_id: str
    query: str = Field(min_length=1)
    mode: str = Field(default="unfiltered", pattern="^(unfiltered|strict_section|heading_boosted)$")
    section_path_prefix: str | None = None
    include_documents: bool = True
    include_artifacts: bool = True
    limit: int = Field(default=10, ge=1, le=50)


class RetrievalCitation(BaseModel):
    source_type: str
    source_id: str
    title: str
    heading_path_text: str | None = None
    section_path: str | None = None


class RetrievalResult(BaseModel):
    source_type: str
    source_id: str
    title: str
    text: str
    score: float
    lexical_score: float
    vector_score: float | None
    confidence: str
    citation: RetrievalCitation


class RetrievalResponse(BaseModel):
    query: str
    mode: str
    degraded: bool
    diagnostics: list[str]
    results: list[RetrievalResult]
