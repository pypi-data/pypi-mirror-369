from _typeshed import Incomplete


class BlockingJobQueue:
    max_workers: Incomplete
    executor: Incomplete
    jobs: Incomplete

    def __init__(self, mode: str = ..., max_workers: int = ...) -> None:
        ...

    def has_room(self):
        ...

    def wait_until_finished(self, desc: Incomplete | None = ...) -> None:
        ...

    def submit(self, func, *args, **kwargs):
        ...


def coerce_num_workers(num_workers: int | str = 'auto',
                       minimum: int = 0) -> int:
    ...
