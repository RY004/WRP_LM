"""Orchestrator worker entrypoint."""

from cortex.workers.queues import ORCHESTRATOR_QUEUES


def main() -> tuple[str, ...]:
    return ORCHESTRATOR_QUEUES


if __name__ == "__main__":
    print(",".join(main()))
