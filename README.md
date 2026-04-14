# Cortex

Cortex is a self-hosted, multi-tenant platform designed to act as an LLM brain and delivery system across wiki, RAG, MCP, pipeline orchestration, and agent-assisted workflows.

The project is being defined through a QRSPI pipeline. Requirements, research, and design are already captured in the project MCP artifacts, and the pipeline is currently in the `structure` stage.

## What Cortex Is

WRP_LM is intended to provide:

- MCP interfaces for Claude/OpenAI-style workflows
- VS Code agent integration
- an LLM wiki
- RAG ingestion and retrieval
- QRSPI pipeline orchestration
- a frontend chatbot
- multi-tenant org/project access control

## Locked v1 Direction

The current design direction is:

- FastAPI backend
- PostgreSQL + `pgvector` as the system of record
- Redis-backed worker runtime
- Google OAuth authentication
- RBAC plus project-level ACL authorization
- native Notion OAuth/API for read-only ingestion
- BGE-M3 embeddings on CPU workers
- hybrid retrieval using lexical search plus dense vector search
- normalized artifact JSON as the canonical editable format, with markdown as a rendered projection

## Core Product Capabilities

- Multi-tenant organizations, users, and projects
- Artifact-driven QRSPI lifecycle with stage gating and approvals
- Section-aware document parsing and retrieval
- Hybrid search with strict section filter, heading-boosted, and unfiltered modes
- Plugin domains for `pipeline`, `wiki`, and `rag`
- Commenting, notifications, and controlled collaboration
- Manual artifact export for user-driven Notion import

## Architecture Summary

The current design breaks the platform into these major areas:

- API/control plane: auth, access control, projects, artifacts, pipeline, plugins, audit
- retrieval plane: documents, sections, chunks, embeddings, ranking, confidence scoring
- worker plane: parsing, embedding, reindexing, Notion sync, exports, remediation, notifications
- integration plane: MCP, VS Code agents, frontend, and Notion connector

Key design choices already made:

- PostgreSQL row-level security protects tenant-bound data
- Docling is the primary parser for PDF, DOCX, and Markdown
- Tree-sitter is used for code snapshot parsing
- JSON is parsed natively
- plugin tools must call internal APIs rather than write directly to persistence layers

## Current Pipeline Status

The project planning pipeline has progressed through:

- Questions
- Research
- Design

Current stage:

- `structure`

Notable planning artifacts already created in the pipeline include:

- canonical requirements briefing
- research report
- research-to-design briefing
- design specification
- design-to-structure briefing

## Repository Status

This repository is currently planning-first. It contains project scaffolding and artifacts, but the implementation work has not been built out yet.

At this point, the repo should be treated as:

- a source of project context
- a home for pipeline-aligned planning outputs
- the future implementation root for the Cortex platform

## Planned v1 Scope

Included in v1:

- stage branching
- sophisticated template builder support
- RAG confidence scoring and quality analytics
- portfolio/export features
- presence and comments as the real-time collaboration baseline
- advanced orchestration support
- multi-phase implementation flow with per-phase artifacts

Out of scope in v1:

- cross-organization sharing
- public plugin marketplace
- automatic approval timeout progression
- full live co-editing
- enterprise certification/compliance programs

## Expected Major Subsystems

Implementation is expected to cover:

- auth and tenancy
- project and ACL management
- artifact storage and versioning
- pipeline state and approvals
- parser adapters
- retrieval and ranking
- embedding workers
- Notion sync
- plugin gateway
- frontend and chatbot surface
- MCP and VS Code integration paths

## Notes

- Notion support is ingestion-only in v1 and remains read-only.
- Artifact editing is designed around normalized structured documents and field-level merge behavior.
- The frontend is expected to support artifact downloads and manual markdown export for Notion import.

## Next Step

The next planning milestone is the `structure` stage, where the design will be translated into package, module, file, and worker layout decisions for implementation.
