"""API models for documents."""

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    project_id: str
    title: str = Field(min_length=1, max_length=255)
    source_kind: str = Field(default="upload", max_length=64)


class SourceUploadCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    media_type: str = Field(default="application/octet-stream", max_length=160)
    content_base64: str


class ReindexCreate(BaseModel):
    reason: str | None = None


class DocumentRead(BaseModel):
    id: str
    project_id: str
    title: str
    source_kind: str
    status: str
    current_version_id: str | None
    current_version_number: int

    model_config = {"from_attributes": True}


class DocumentVersionRead(BaseModel):
    id: str
    document_id: str
    source_id: str
    version_number: int
    parse_status: str
    parser_name: str | None
    normalized_tree: dict
    rendered_markdown: str
    diagnostics_summary: dict

    model_config = {"from_attributes": True}


class DocumentSourceRead(BaseModel):
    id: str
    document_id: str
    storage_uri: str
    storage_key: str
    filename: str
    media_type: str
    size_bytes: int | None
    checksum: str | None

    model_config = {"from_attributes": True}


class ParseJobRead(BaseModel):
    id: str
    document_version_id: str
    queue_name: str
    status: str
    attempts: int
    last_error: str | None

    model_config = {"from_attributes": True}


class SourceUploadRead(BaseModel):
    source: DocumentSourceRead
    version: DocumentVersionRead
    parse_job: ParseJobRead


class ReindexRead(BaseModel):
    id: str
    document_id: str
    status: str
    reason: str | None
    queued_parse_job_id: str | None

    model_config = {"from_attributes": True}
