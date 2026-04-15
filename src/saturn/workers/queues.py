"""Central queue ownership for worker entrypoints."""

CPU_QUEUES = ("parse", "embed")
ORCHESTRATOR_QUEUES = ("reindex", "pipeline_remediation")
IO_QUEUES = ("notion_sync", "export", "notifications")
