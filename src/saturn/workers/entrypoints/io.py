"""I/O worker entrypoint."""

from saturn.workers.queues import IO_QUEUES


def main() -> tuple[str, ...]:
    return IO_QUEUES


if __name__ == "__main__":
    print(",".join(main()))
