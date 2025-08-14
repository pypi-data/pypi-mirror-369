from typing import Type
from types import TracebackType
from _typeshed import Incomplete


class Superlock:
    THREAD_LOCKS: Incomplete
    GLOBAL_THREAD_KEY: str
    GLOBAL_APPNAME: str
    GLOBAL_LOCK_FNAME: str
    lock_fpath: Incomplete
    thread_key: Incomplete
    process_lock: Incomplete
    thread_lock: Incomplete

    def __init__(self, lock_fpath=..., thread_key=...) -> None:
        ...

    @property
    def global_lock_fpath(self):
        ...

    def acquire(self,
                blocking: bool = ...,
                timeout: Incomplete | None = ...,
                delay: float = ...,
                max_delay: float = ...):
        ...

    def release(self) -> None:
        ...

    def __enter__(self):
        ...

    def __exit__(self, ex_type: Type[BaseException] | None,
                 ex_value: BaseException | None,
                 ex_traceback: TracebackType | None) -> bool | None:
        ...
