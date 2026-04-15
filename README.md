# Saturn

Saturn is a self-hosted, multi-tenant platform for wiki, retrieval, MCP, pipeline orchestration, and agent-assisted workflows.

This repository is the implementation root for the Saturn v1 platform. The current work tree is scaffolded from the approved QRSPI structure and plan artifacts for pipeline project `WRP_LM`.

## Locked Platform Direction

- FastAPI control plane rooted in `src/cortex`
- PostgreSQL with `pgvector`
- Redis-backed worker runtime
- Google OAuth authentication
- RBAC plus project-level ACL authorization
- Native Notion OAuth/API ingestion
- Queue-driven parse, embed, reindex, sync, export, remediation, and notification work
- S3-compatible production blob storage behind `src/cortex/storage/base.py`
- Normalized JSON as the canonical artifact format, with markdown as a rendered projection

## Repository Layout

- `src/cortex/` contains the backend package and worker entrypoints.
- `apps/web/` contains the Next.js product surface.
- `apps/vscode/` contains the VS Code integration surface.
- `migrations/` contains Alembic migration scaffolding.
- `tests/` contains unit, API, integration, worker, migration, and end-to-end test skeletons.

## Current Status

The repository is scaffolded and implementation-ready, but most business logic is still intentionally deferred to later execution phases.
