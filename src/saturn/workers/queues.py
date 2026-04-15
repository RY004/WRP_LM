"""Central queue ownership for worker entrypoints."""

CPU_QUEUES = ("parse", "embed")
ORCHESTRATOR_QUEUES = ("reindex", "pipeline_remediation")
IO_QUEUES = ("notion_sync", "export", "notifications")

WORKER_QUEUE_MAP = {
    "cpu": CPU_QUEUES,
    "orchestrator": ORCHESTRATOR_QUEUES,
    "io": IO_QUEUES,
}

ALL_QUEUES = CPU_QUEUES + ORCHESTRATOR_QUEUES + IO_QUEUES


def queues_for_worker(worker_name: str) -> tuple[str, ...]:
    return WORKER_QUEUE_MAP[worker_name]
