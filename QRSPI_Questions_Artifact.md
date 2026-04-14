---
project: QRSPI Pipeline MCP
stage: questions
version: 1
status: complete
created: 2026-04-01
author: Colin Bow
next_stage: research
handoff_to_research:
  - This document (full Q&A with all decisions and constraints)
  - Research should investigate: MCP SDK patterns for multi-tool servers, flat-file artifact storage patterns, SQLite state machine implementations, YAML frontmatter indexing approaches, pipeline/workflow engine prior art, multi-tenant file-based systems
---

# Questions Artifact — QRSPI Pipeline MCP

## Project Identity

**Project Name:** QRSPI Pipeline MCP
**Project Type:** Full (all stages)
**Owner:** Colin Bow
**Description:** A Model Context Protocol server that implements QRSPI — a structured, stage-gated project lifecycle framework for AI-assisted development. Claude interacts with the pipeline natively through MCP tools, producing artifacts at each stage, enforcing alignment before execution, and maintaining a complete audit trail from idea to implementation.

---

## 1. Problem Definition

### What problem does this solve?

AI-assisted development fails when Claude guesses or assumes instead of working from explicit, documented intent. The pipeline enforces structured alignment (Questions → Research → Design → Structure → Plan) before any execution begins (Work Tree → Implement → PR Review). Every stage produces artifacts that constrain and inform subsequent stages. The result is less rework, fewer misaligned outputs, and a traceable decision history.

### What is the single biggest pain point?

Scope drift and context loss. Without a structured pipeline, Claude operates on incomplete or assumed context, producing work that doesn't match the user's actual goals. The pipeline forces explicit articulation at every step and ensures each stage is aware of what the next stage needs.

### What does "done" look like for v1?

A working MCP server that Claude can connect to and run a real project through end-to-end. All stages functional. All core tools operational. A user can create a project, move through all 8 stages, produce artifacts at each, and complete with a PR Review that traces back to the original Questions.

---

## 2. Users & Access

### Who is this for?

Colin (primary), plus friends and collaborators. Multi-tenant from day one.

### Access hierarchy

Orgs → Teams → Projects, and Personal → Projects. Auth is delegated to the existing RAG server auth framework. The pipeline MCP validates against the same user store — it does not implement its own auth.

### Collaborator access model

- Collaborators who join mid-pipeline see the full artifact history.
- Parallel work is allowed between independent stages (stages whose dependencies are already satisfied).
- Within a single stage (e.g., Implementation), parallel task work is allowed on independent tasks.
- Dependent stages cannot be worked in parallel (Design must complete before Structure can begin).

### Pipeline template visibility

Templates are shared within orgs. Other orgs cannot see or clone them.

---

## 3. Architecture Decisions

### Storage model: Hybrid

- **Artifacts:** Flat Markdown files with YAML frontmatter on the server filesystem. Human-readable, LLM-readable, browsable in VS Code.
- **Pipeline state:** SQLite database for project metadata, stage transitions, time logs, user/team mappings, and queryable state.
- **Work Tree outputs:** Separate `/outputs/` directory per project for downloadable scaffolding, code, and config files that users can manually push to GitHub.
- **Filesystem layout:** To be determined in Structure stage.

### Artifact format

Markdown with YAML frontmatter. Frontmatter contains metadata (stage, version, project_id, dependencies, status, timestamps). Body is structured Markdown with consistent heading hierarchies. The MCP indexes frontmatter for queries while the body stays LLM-readable.

### Artifact immutability

Artifacts from completed stages are never edited. If downstream stages discover flaws, a new amendment or issue artifact is created in the current stage, referencing the original. This preserves the audit trail. Amendments require HITL approval before they update Alignment artifacts.

### Artifact types (fixed set)

Stages select from predefined artifact types. Custom pipelines configure which types each stage produces but cannot define new types. The fixed set includes: Markdown document, structured Q&A, technology options matrix, design specification, file tree specification, execution plan, code output, amendment proposal, issue report, review checklist, briefing note, changelog entry.

---

## 4. Pipeline Model

### Default pipeline: QRSPI

**Alignment Phase:** Questions → Research → Design → Structure → Plan
**Execution Phase:** Work Tree → Implement → PR Review

### Execution cycles

A pipeline supports multiple execution cycles (W-I-PR) against a stable Alignment base. Each cycle starts fresh from the Alignment artifacts — no inheriting previous cycle's Implementation artifacts. Cycles are numbered (Cycle 1, Cycle 2, etc.) with independent artifact sets.

### Re-entrant execution stages

For production pipelines (e.g., news scraper + post builder), execution stages can run independently after initial Alignment. Each run produces new outputs without re-running Alignment. These pipelines may depend on external MCP servers the user has built (e.g., a news database MCP). The pipeline MCP doesn't call those servers — the stage instructions tell Claude to expect data from those sources via the user.

### Custom pipelines

Users can create custom pipeline templates with different stages, different exit criteria, and different depth. The pipeline builder tool walks users through stage definition interactively. Pipeline templates include stage-aware system prompts (Claude's persona per stage), not just artifact configurations.

### Preset project types

Predefined pipeline templates for common scenarios (full project, feature, bugfix, content creation, research-only, etc.). Users can also create and save their own.

---

## 5. Stage Behavior Model

### Stage isolation (three-input model)

Each stage receives exactly three inputs and nothing else:

1. **Handoff packet** from the previous stage — the specific artifacts tagged for downstream consumption, defined in the pipeline template. Includes a natural language briefing note summarizing what was decided and what this stage should focus on.
2. **Stage instructions** — what to do, what persona Claude adopts, what artifacts to produce, what exit criteria to meet.
3. **Next-stage requirements** — a checklist of what the next stage will expect as input. Claude uses this for forward-looking awareness so it produces everything downstream needs.

Stages do NOT receive full project context. They do not see artifacts from two stages back unless those were explicitly included in the handoff packet.

### Handoff packets

Defined in pipeline templates and stage instructions, not dynamically selected by Claude. Each stage has a predefined list of what it passes to the next stage.

### Claude's proactive behavior

- **Default mode: Blocking prompts.** Claude will not advance a stage with unresolved gaps. It identifies what's missing and requires resolution before proceeding.
- **Configurable per project.** Lighter projects can be set to gentle nudges instead of hard blocks.
- Claude drives the conversation forward, flags gaps, asks follow-ups, and presents progress summaries at mid-stage checkpoints.

### Mid-stage checkpoints (Proposal F)

During Implementation, after every N tasks (configurable), Claude pauses and presents a progress summary: what's done, what's next, any deviations from Plan. User approves before continuing.

### Exit criteria overrides

Allowed with a logged warning. The warning becomes part of the handoff so downstream stages know something was skipped and can compensate. Not a hard block — a documented risk acceptance.

---

## 6. Amendment System

### How amendments work

When an execution stage (W, I, or PR) discovers a flaw in an Alignment artifact (Q, R, D, S, or P), it creates a formal amendment proposal artifact. The pipeline pauses. The human reviews the proposal and either approves (updating the Alignment artifact with a new version) or rejects. No parallel work continues while an amendment is pending. After approval, the fix is applied, and the pipeline resumes from the current stage.

---

## 7. MCP Tool Organization

### Context cascade (Proposal H)

The MCP's tool documentation follows a hierarchical skill tree pattern to minimize context usage:

```
QRSPI.md (root overview, compact)
├── alignment/
│   ├── README.md (phase overview)
│   ├── questions.md (stage tools, persona, exit criteria)
│   ├── research.md
│   ├── design.md
│   ├── structure.md
│   └── plan.md
├── execution/
│   ├── README.md
│   ├── worktree.md
│   ├── implement.md
│   └── pr_review.md
├── tools/
│   ├── project_management.md
│   ├── artifact_management.md
│   ├── analytics.md
│   └── pipeline_builder.md
└── templates/
    └── (user-created pipeline templates)
```

Claude reads the root SKILL.md first, then drills into the relevant stage or tool category. Only the necessary context is loaded per tool call.

### Tool surface

Wide from v1. All core tools operational at launch. Tools are organized into categories: project management, artifact management, stage-specific, intelligence/meta, and analytics.

---

## 8. Integrations

### GitHub

Secondary concern. Claude Desktop produces artifacts (scaffolding, code, configs) that users download and push manually. The MCP does not interact with GitHub directly. Claude Code could eventually execute git operations, but that's outside the pipeline MCP's scope.

### External MCPs during Research

Claude can use its native web search and any third-party MCPs connected to the session during the Research stage. The pipeline MCP itself does not call external services. The user's custom MCPs (Study, SEC, News) are not called by the pipeline MCP — if users want that data, they bring it in during Questions or paste it into the Research conversation.

### External MCPs for re-entrant execution

Custom production pipelines (news scraper, etc.) may require data from external MCPs the user has built. The pipeline stage instructions reference those sources, but the pipeline MCP doesn't invoke them. The user provides the data in the conversation.

---

## 9. Error & Lifecycle States

### Error handling

- Exit criteria failures: override allowed with logged warning, warning propagates in handoff.
- Amendment pending: pipeline pauses until HITL resolves.
- Blocked stage: any stage can enter blocked state with a reason, tracked and surfaced in status queries.

### Project lifecycle

- **Active:** pipeline in progress.
- **Paused:** user stepped away, pipeline frozen in current state.
- **Completed:** all stages finished, pipeline archived.
- **Abandoned → Paused:** no automatic deletion. User can delete pipeline, delete artifacts only (restart), or delete both.

---

## 10. Anti-Goals

What this project is NOT:

- **Not a full PM tool.** Not Jira, not Linear, not Asana. No sprint management, no burndown charts, no team velocity tracking beyond pipeline-scoped analytics.
- **Not a CI/CD pipeline.** Does not build, test, or deploy code. Produces artifacts that humans or other tools act on.
- **Not an agentic orchestrator.** The pipeline MCP does not call other MCP servers, does not invoke external APIs, does not execute code on the server. It structures conversations and stores artifacts.
- **Not a team collaboration platform.** Multi-tenant access exists, but this is not Slack, not Notion, not a real-time collaboration tool. It's a structured project lifecycle that multiple people can contribute to.

---

## 11. Feature Inventory (Confirmed for Build)

### v1 — Core Pipeline

- Project CRUD with multi-tenant support (orgs, teams, personal)
- QRSPI stage state machine with validated transitions
- Artifact storage (flat Markdown files with YAML frontmatter)
- Pipeline state database (SQLite)
- Stage-aware system prompts / personas
- Stage exit criteria enforcement with override + logged warning
- Human gate review at Alignment-to-Execution boundary
- Three-input stage isolation model (handoff packet, stage instructions, next-stage requirements)
- Handoff packets with briefing notes
- Decision log (append-only, per project)
- Assumption tracker (created in Q/R, verified in PR)
- Risk register (created in D, verified in PR)
- Amendment proposal system with HITL approval
- Time tracking (stage entry/exit timestamps)
- Blocking proactive behavior (configurable per project)
- Mid-stage checkpoints during Implementation
- Artifact dependency tracking and staleness flags
- Context cascade tool documentation (hierarchical skill tree)
- Execution cycles (multiple W-I-PR rounds against stable Alignment)
- Work Tree file outputs in separate `/outputs/` directory
- Three-axis PR review (Plan, Design, Questions compliance)
- PR body auto-generation
- Session briefing tool (Proposal A)
- Stage forward-awareness / next-stage requirements (Proposal E)
- Wide MCP tool surface across all 5 categories

### v2 — Intelligence & Templates

- Artifact versioning with diffs
- Stage branching for parallel exploration
- Pipeline template system with builder tool (Proposal G)
- Preset project types (full, feature, bugfix, content, research-only)
- Shareable templates within orgs
- Confidence scoring per artifact
- Project DNA (compact context injection)
- Feedback loops from PR to earlier stages
- Changelog auto-generation
- Export to deliverable (Word, PDF, Markdown bundle)
- Quality scoring per artifact over time
- Pipeline velocity analytics
- Dashboard web endpoint
- Git-native artifact storage option
- Test plan integration
- Retrospective stage
- Excel artifact support (Proposal B)
- Portfolio export mode (Proposal C)
- Execution cycle dashboard (Proposal I)

### v3 — Advanced

- Claude-as-PM orchestrator mode
- Multi-agent stage personas
- Cross-project pattern detection
- Searchable knowledge base across completed pipelines
- Webhook/notification system
- Multi-user real-time collaboration
- Feedback refinement mini-pipelines
- Stage skip correlation analysis
- Naming convention engine with thematic codenames (Proposal D)

---

## 12. Open Items (Deferred to Later Stages)

- Exact filesystem layout for artifacts and outputs (Structure stage)
- SQLite schema design (Design stage)
- Artifact type JSON schemas (Design stage)
- MCP tool parameter specifications (Design stage)
- Pipeline template schema (Design stage)
- Port assignment on server (Structure stage)
- Specific exit criteria checklists per QRSPI stage (Design stage)
- Handoff packet contents per stage pair (Design stage)
- Stage persona prompt text (Design stage)

---

## Briefing Note for Research Stage

This project is a FastAPI-based MCP server implementing a structured project pipeline called QRSPI. The core challenge is building a stage-gated state machine with flat-file artifact storage, a three-input stage isolation model, and a hierarchical tool documentation system — all exposed as MCP tools over Tailscale.

Research should investigate: existing MCP server patterns for complex multi-tool servers, flat-file storage systems with YAML frontmatter indexing, SQLite-backed state machines in Python, pipeline/workflow engine architectures (particularly stage-gated models), multi-tenant file-based storage patterns, and how other developer tools implement context cascading for large tool surfaces. Research should also look at whether there are existing pipeline frameworks (like Prefect, Dagster, or similar) whose patterns are worth borrowing even though we're not building a data pipeline.
