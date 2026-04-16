"""Repository layer for embeddings."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from saturn.embeddings.db_models import EmbeddingJob, EmbeddingRecord


class EmbeddingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, model):
        self.session.add(model)
        return model

    def upsert_record(
        self,
        project_id: str,
        source_type: str,
        source_id: str,
        source_version_id: str | None,
        model_name: str,
        dimensions: int,
        vector: list[float],
        text_hash: str,
    ) -> EmbeddingRecord:
        record = self.session.scalar(
            select(EmbeddingRecord).where(
                EmbeddingRecord.source_type == source_type,
                EmbeddingRecord.source_id == source_id,
                EmbeddingRecord.model_name == model_name,
            )
        )
        if record is None:
            record = EmbeddingRecord(
                project_id=project_id,
                source_type=source_type,
                source_id=source_id,
                source_version_id=source_version_id,
                model_name=model_name,
                dimensions=dimensions,
                vector=vector,
                text_hash=text_hash,
            )
            self.session.add(record)
            return record
        record.project_id = project_id
        record.source_version_id = source_version_id
        record.dimensions = dimensions
        record.vector = vector
        record.text_hash = text_hash
        record.status = "ready"
        return record

    def list_records(self, project_id: str, model_name: str | None = None) -> list[EmbeddingRecord]:
        stmt = select(EmbeddingRecord).where(EmbeddingRecord.project_id == project_id)
        if model_name:
            stmt = stmt.where(EmbeddingRecord.model_name == model_name)
        return list(self.session.scalars(stmt))

    def records_by_source(self, project_id: str, model_name: str | None = None) -> dict[tuple[str, str], EmbeddingRecord]:
        return {
            (record.source_type, record.source_id): record
            for record in self.list_records(project_id, model_name=model_name)
        }

    def get_job(self, job_id: str) -> EmbeddingJob | None:
        return self.session.get(EmbeddingJob, job_id)
