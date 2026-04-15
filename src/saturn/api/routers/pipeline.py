"""Pipeline router scaffold."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])
