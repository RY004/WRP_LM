"""Application container scaffold."""

from dataclasses import dataclass

from cortex.bootstrap.settings import Settings


@dataclass(slots=True)
class ApplicationContainer:
    settings: Settings
