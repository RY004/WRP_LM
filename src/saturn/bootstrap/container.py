"""Application container scaffold."""

from dataclasses import dataclass

from saturn.bootstrap.settings import Settings


@dataclass(slots=True)
class ApplicationContainer:
    settings: Settings
