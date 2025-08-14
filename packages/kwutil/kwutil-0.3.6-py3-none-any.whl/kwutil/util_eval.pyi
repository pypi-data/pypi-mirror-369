from typing import Dict
from typing import Any
from typing import List
import ast
from _typeshed import Incomplete


class RestrictedSyntaxError(Exception):
    ...


def restricted_eval(expr: str,
                    max_chars: int = ...,
                    local_dict: Dict[str, Any] | None = None,
                    builtins_passlist: List[str] | None = None):
    ...


class EvalException(Exception):
    ...


class ValidationException(EvalException):
    ...


class CompilationException(EvalException):
    exc: Incomplete

    def __init__(self, exc) -> None:
        ...


class ExecutionException(EvalException):
    exc: Incomplete

    def __init__(self, exc) -> None:
        ...


class SafeAST(ast.NodeVisitor):
    allowed: Incomplete
    allowed_funcs: Incomplete
    allowed_attrs: Incomplete

    def __init__(self,
                 safenodes: Incomplete | None = ...,
                 addnodes: Incomplete | None = ...,
                 funcs: Incomplete | None = ...,
                 attrs: Incomplete | None = ...) -> None:
        ...

    def generic_visit(self, node) -> None:
        ...


def evalidate(expression,
              safenodes: Incomplete | None = ...,
              addnodes: Incomplete | None = ...,
              funcs: Incomplete | None = ...,
              attrs: Incomplete | None = ...):
    ...


def safeeval(expression,
             context=...,
             safenodes: List[str] | None = None,
             addnodes: List[str] | None = None,
             funcs: List[str] | None = None,
             attrs: List[str] | None = None) -> Any:
    ...
