"""CPU worker entrypoint."""

from saturn.workers.queues import CPU_QUEUES


def main() -> tuple[str, ...]:
    return CPU_QUEUES


if __name__ == "__main__":
    print(",".join(main()))
