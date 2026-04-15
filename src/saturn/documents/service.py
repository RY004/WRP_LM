"""Service layer for documents."""

import base64
import hashlib
import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from saturn.access.context import AuthContext
from saturn.access.policies import Permission, require_authenticated
from saturn.access.service import AccessService
from saturn.documents.db_models import (
    Document,
    DocumentChunk,
    DocumentParseJob,
    DocumentReindexRequest,
    DocumentSection,
    DocumentSource,
    DocumentVersion,
    ParseDiagnostic,
)
from saturn.documents.parsing.adapters.base import ParsedSection
from saturn.documents.parsing.chunking import chunk_section_text
from saturn.documents.parsing.registry import ParserRegistry, default_parser_registry
from saturn.documents.parsing.section_paths import heading_path_ltree, heading_path_text
from saturn.documents.repository import DocumentRepository
from saturn.shared.ids import new_id
from saturn.shared.time import utc_now
from saturn.storage.base import StorageBackend


@dataclass(slots=True)
class ParseMaterialization:
    sections: list[DocumentSection]
    chunks: list[DocumentChunk]
    diagnostics: list[ParseDiagnostic]


class DocumentService:
    def __init__(
        self,
        session: Session,
        storage: StorageBackend | None = None,
        parser_registry: ParserRegistry | None = None,
    ) -> None:
        self.session = session
        self.storage = storage
        self.parsers = parser_registry or default_parser_registry()
        self.repository = DocumentRepository(session)
        self.access = AccessService(session)

    def register_document(
        self, context: AuthContext, project_id: str, title: str, source_kind: str = "upload"
    ) -> Document:
        user_id = require_authenticated(context)
        self.access.require_project_permission(context, project_id, Permission.PROJECT_WRITE)
        document = Document(
            project_id=project_id,
            title=title,
            source_kind=source_kind,
            created_by_user_id=user_id,
            updated_by_user_id=user_id,
        )
        return self.repository.add(document)

    def list_documents(self, context: AuthContext, project_id: str) -> list[Document]:
        self.access.require_project_permission(context, project_id, Permission.PROJECT_READ)
        return self.repository.list_documents(project_id)

    def get_document(self, context: AuthContext, document_id: str) -> Document:
        document = self.repository.get_document(document_id)
        if document is None:
            raise LookupError("Document not found")
        self.access.require_project_permission(context, document.project_id, Permission.PROJECT_READ)
        return document

    def register_source_upload(
        self,
        context: AuthContext,
        document_id: str,
        filename: str,
        media_type: str,
        payload: bytes,
    ) -> tuple[DocumentSource, DocumentVersion, DocumentParseJob]:
        if self.storage is None:
            raise ValueError("Storage backend is required for source upload")
        user_id = require_authenticated(context)
        document = self.get_document(context, document_id)
        self.access.require_project_permission(context, document.project_id, Permission.PROJECT_WRITE)
        checksum = hashlib.sha256(payload).hexdigest()
        next_version = document.current_version_number + 1
        key = (
            f"documents/{document.project_id}/{document.id}/sources/v{next_version}/"
            f"{checksum[:16]}-{_safe_filename(filename)}"
        )
        descriptor = self.storage.write_bytes(key, payload)
        source = DocumentSource(
            document_id=document.id,
            storage_uri=descriptor.uri,
            storage_key=descriptor.key,
            filename=filename,
            media_type=media_type,
            size_bytes=descriptor.size_bytes,
            checksum=checksum,
            created_by_user_id=user_id,
        )
        self.repository.add(source)
        self.session.flush()
        version = DocumentVersion(
            document_id=document.id,
            source_id=source.id,
            version_number=next_version,
            parse_status="pending",
            created_by_user_id=user_id,
        )
        self.repository.add(version)
        self.session.flush()
        document.current_version_id = version.id
        document.current_version_number = version.version_number
        document.status = "pending_parse"
        document.updated_by_user_id = user_id
        job = DocumentParseJob(document_version_id=version.id, queue_name="parse", status="queued")
        self.repository.add(job)
        self.session.flush()
        return source, version, job

    def register_source_upload_base64(
        self,
        context: AuthContext,
        document_id: str,
        filename: str,
        media_type: str,
        content_base64: str,
    ) -> tuple[DocumentSource, DocumentVersion, DocumentParseJob]:
        return self.register_source_upload(
            context,
            document_id,
            filename,
            media_type,
            base64.b64decode(content_base64),
        )

    def request_reindex(
        self, context: AuthContext, document_id: str, reason: str | None = None
    ) -> DocumentReindexRequest:
        user_id = require_authenticated(context)
        document = self.get_document(context, document_id)
        self.access.require_project_permission(context, document.project_id, Permission.PROJECT_WRITE)
        request = DocumentReindexRequest(
            document_id=document.id,
            requested_by_user_id=user_id,
            status="queued",
            reason=reason,
        )
        return self.repository.add(request)

    def create_parse_job_for_current_version(self, document_id: str) -> DocumentParseJob:
        document = self.repository.get_document(document_id)
        if document is None or not document.current_version_id:
            raise LookupError("Document current version not found")
        job = DocumentParseJob(
            document_version_id=document.current_version_id,
            queue_name="parse",
            status="queued",
        )
        return self.repository.add(job)

    def parse_version(self, version_id: str) -> DocumentVersion:
        if self.storage is None:
            raise ValueError("Storage backend is required for parsing")
        version = self.repository.get_version(version_id)
        if version is None:
            raise LookupError("Document version not found")
        source = self.repository.get_source(version.source_id)
        if source is None:
            raise LookupError("Document source not found")
        document = self.repository.get_document(version.document_id)
        if document is None:
            raise LookupError("Document not found")
        version.parse_status = "parsing"
        document.status = "parsing"
        payload = self.storage.read_bytes(source.storage_key)
        parser = self.parsers.parser_for(source.filename, source.media_type)
        output = parser.parse(payload, source.filename, source.media_type)
        materialized = self._materialize(version.id, output.sections, output.diagnostics)
        self.repository.replace_parse_rows(
            version.id,
            materialized.sections,
            materialized.chunks,
            materialized.diagnostics,
        )
        version.parser_name = output.parser_name
        version.normalized_tree = output.normalized_tree
        version.rendered_markdown = output.rendered_markdown
        version.parse_status = output.status
        version.diagnostics_summary = {
            "count": len(output.diagnostics),
            "errors": sum(1 for item in output.diagnostics if item.severity == "error"),
            "warnings": sum(1 for item in output.diagnostics if item.severity == "warning"),
        }
        version.parsed_at = utc_now()
        document.status = output.status
        return version

    def mark_parse_failed(self, version_id: str, message: str) -> DocumentVersion:
        version = self.repository.get_version(version_id)
        if version is None:
            raise LookupError("Document version not found")
        document = self.repository.get_document(version.document_id)
        version.parse_status = "failed"
        version.diagnostics_summary = {"count": 1, "errors": 1, "warnings": 0}
        self.repository.replace_parse_rows(
            version.id,
            [],
            [],
            [
                ParseDiagnostic(
                    document_version_id=version.id,
                    severity="error",
                    code="parse_job_failed",
                    message=message,
                    details={},
                )
            ],
        )
        if document is not None:
            document.status = "failed"
        return version

    def _materialize(self, version_id: str, roots: list[ParsedSection], diagnostics) -> ParseMaterialization:
        sections: list[DocumentSection] = []
        chunks: list[DocumentChunk] = []
        diagnostic_rows = [
            ParseDiagnostic(
                document_version_id=version_id,
                severity=item.severity,
                code=item.code,
                message=item.message,
                details=item.details,
            )
            for item in diagnostics
        ]
        ordinal = 0

        def visit(section: ParsedSection, path: list[str], parent_id: str | None = None) -> None:
            nonlocal ordinal
            ordinal += 1
            current_path = path + [section.title]
            text_path = heading_path_text(current_path)
            ltree_path = heading_path_ltree(current_path)
            section_id = new_id()
            row = DocumentSection(
                id=section_id,
                document_version_id=version_id,
                parent_section_id=parent_id,
                ordinal=ordinal,
                level=section.level,
                title=section.title,
                body=section.body,
                heading_path_text=text_path,
                heading_path_ltree=ltree_path,
                metadata_json=section.metadata,
            )
            sections.append(row)
            for chunk in chunk_section_text(section.body, text_path, ltree_path, ordinal):
                chunks.append(
                    DocumentChunk(
                        document_version_id=version_id,
                        section_id=section_id,
                        ordinal=len(chunks) + 1,
                        text=chunk.text,
                        heading_path_text=chunk.heading_path_text,
                        heading_path_ltree=chunk.heading_path_ltree,
                        token_count_estimate=chunk.token_count_estimate,
                        metadata_json=chunk.metadata,
                    )
                )
            for child in section.children:
                visit(child, current_path, section_id)

        for root in roots:
            visit(root, [])
        return ParseMaterialization(sections=sections, chunks=chunks, diagnostics=diagnostic_rows)


def _safe_filename(filename: str) -> str:
    name = filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return safe or "source.bin"
