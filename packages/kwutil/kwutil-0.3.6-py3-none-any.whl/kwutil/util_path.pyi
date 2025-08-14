from typing import List
import ubelt as ub
from os import PathLike
from typing import Dict
from _typeshed import Incomplete
from collections.abc import Generator
from typing import Any


def tree(path) -> Generator[str, None, None]:
    ...


def coerce_patterned_paths(data: str | List[str],
                           expected_extension: Incomplete | None = ...,
                           globfallback: bool = False) -> List[ub.Path]:
    ...


def find(pattern: str | None = None,
         dpath: str | None = None,
         include: str | List[str] | None = None,
         exclude: str | List[str] | None = None,
         type: str | List[str] | None = None,
         recursive: bool = ...,
         followlinks: bool = False) -> Generator[Any, None, Any]:
    ...


def resolve_relative_to(path, dpath, strict: bool = ...):
    ...


def resolve_directory_symlinks(path):
    ...


def sidecar_glob(
        main_pat: str | PathLike,
        sidecar_ext,
        main_key: str = ...,
        sidecar_key: Incomplete | None = ...,
        recursive: int = ...
) -> Generator[Dict[str, ub.Path | None], None, None]:
    ...
