"""Plugins router scaffold."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/plugins", tags=["plugins"])
