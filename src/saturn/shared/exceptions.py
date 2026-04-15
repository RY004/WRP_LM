"""Shared exception types."""


class SaturnError(Exception):
    def __init__(self, detail: str, status_code: int = 400) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


class ConfigurationError(SaturnError):
    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail, status_code=500)


class NotFoundError(SaturnError):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(detail=detail, status_code=404)


class StorageError(SaturnError):
    def __init__(self, detail: str) -> None:
        super().__init__(detail=detail, status_code=500)
