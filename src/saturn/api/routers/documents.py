"""Document intake routes."""

from fastapi import APIRouter

from saturn.api.deps import AuthContextDep, DbSessionDep, StorageDep
from saturn.documents.api_models import (
    DocumentCreate,
    DocumentRead,
    DocumentVersionRead,
    ReindexCreate,
    ReindexRead,
    SourceUploadCreate,
    SourceUploadRead,
)
from saturn.documents.service import DocumentService

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("", response_model=DocumentRead, status_code=201)
async def create_document(
    payload: DocumentCreate, context: AuthContextDep, session: DbSessionDep
) -> DocumentRead:
    document = DocumentService(session).register_document(
        context,
        project_id=payload.project_id,
        title=payload.title,
        source_kind=payload.source_kind,
    )
    session.commit()
    return DocumentRead.model_validate(document)


@router.get("/projects/{project_id}", response_model=list[DocumentRead])
async def list_project_documents(
    project_id: str, context: AuthContextDep, session: DbSessionDep
) -> list[DocumentRead]:
    service = DocumentService(session)
    return [DocumentRead.model_validate(document) for document in service.list_documents(context, project_id)]


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: str, context: AuthContextDep, session: DbSessionDep
) -> DocumentRead:
    return DocumentRead.model_validate(DocumentService(session).get_document(context, document_id))


@router.post("/{document_id}/sources", response_model=SourceUploadRead, status_code=201)
async def register_source_upload(
    document_id: str,
    payload: SourceUploadCreate,
    context: AuthContextDep,
    session: DbSessionDep,
    storage: StorageDep,
) -> SourceUploadRead:
    source, version, parse_job = DocumentService(session, storage=storage).register_source_upload_base64(
        context,
        document_id=document_id,
        filename=payload.filename,
        media_type=payload.media_type,
        content_base64=payload.content_base64,
    )
    session.commit()
    return SourceUploadRead(
        source=source,
        version=version,
        parse_job=parse_job,
    )


@router.get("/{document_id}/versions", response_model=list[DocumentVersionRead])
async def list_document_versions(
    document_id: str, context: AuthContextDep, session: DbSessionDep
) -> list[DocumentVersionRead]:
    service = DocumentService(session)
    document = service.get_document(context, document_id)
    return [
        DocumentVersionRead.model_validate(version)
        for version in service.repository.list_versions(document.id)
    ]


@router.post("/{document_id}/reindex", response_model=ReindexRead, status_code=202)
async def request_reindex(
    document_id: str,
    payload: ReindexCreate,
    context: AuthContextDep,
    session: DbSessionDep,
) -> ReindexRead:
    request = DocumentService(session).request_reindex(context, document_id, payload.reason)
    session.commit()
    return ReindexRead.model_validate(request)
