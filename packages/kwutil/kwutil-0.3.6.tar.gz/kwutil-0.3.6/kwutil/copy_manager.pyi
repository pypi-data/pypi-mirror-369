from typing import Type
from types import TracebackType
from os import PathLike
from _typeshed import Incomplete


class CopyManager:
    eager: Incomplete

    def __init__(self,
                 workers: int = ...,
                 mode: str = ...,
                 eager: bool = ...) -> None:
        ...

    def __enter__(self):
        ...

    def __len__(self) -> int:
        ...

    def __exit__(self, ex_type: Type[BaseException] | None,
                 ex_value: BaseException | None,
                 ex_traceback: TracebackType | None) -> bool | None:
        ...

    def submit(self,
               src: str | PathLike,
               dst: str | PathLike,
               overwrite: bool = False,
               skip_existing: bool = ...) -> None:
        ...

    def run(self,
            desc: str | None = None,
            verbose: int = ...,
            pman: Incomplete | None = ...) -> None:
        ...
