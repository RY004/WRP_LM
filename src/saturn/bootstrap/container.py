"""Application dependency container."""

from dataclasses import dataclass, field

from sqlalchemy.orm import Session, sessionmaker

from saturn.bootstrap.settings import Settings
from saturn.db.session import create_session_factory
from saturn.shared.exceptions import ConfigurationError
from saturn.storage.base import StorageBackend
from saturn.storage.filesystem import FilesystemStorage
from saturn.storage.s3 import S3Storage
from saturn.workers.runtime.broker import WorkerBroker
from saturn.workers.runtime.settings import WorkerRuntimeSettings


@dataclass(slots=True)
class ApplicationContainer:
    settings: Settings
    _session_factory: sessionmaker[Session] | None = field(default=None, init=False, repr=False)
    _storage: StorageBackend | None = field(default=None, init=False, repr=False)
    _worker_broker: WorkerBroker | None = field(default=None, init=False, repr=False)

    @property
    def session_factory(self) -> sessionmaker[Session]:
        if self._session_factory is None:
            self._session_factory = create_session_factory(self.settings)
        return self._session_factory

    def set_session_factory(self, factory: sessionmaker[Session]) -> None:
        self._session_factory = factory

    @property
    def storage(self) -> StorageBackend:
        if self._storage is None:
            if self.settings.storage_backend == "filesystem":
                self._storage = FilesystemStorage(self.settings.storage_filesystem_root)
            elif self.settings.storage_backend == "s3":
                if not self.settings.storage_s3_bucket:
                    raise ConfigurationError("S3 storage requires a configured bucket")
                self._storage = S3Storage(
                    bucket=self.settings.storage_s3_bucket,
                    endpoint_url=self.settings.storage_s3_endpoint,
                    access_key=self.settings.storage_s3_access_key,
                    secret_key=self.settings.storage_s3_secret_key,
                )
            else:
                raise ConfigurationError(f"Unsupported storage backend: {self.settings.storage_backend}")
        return self._storage

    @property
    def worker_broker(self) -> WorkerBroker:
        if self._worker_broker is None:
            self._worker_broker = WorkerBroker(WorkerRuntimeSettings.from_settings(self.settings))
        return self._worker_broker
