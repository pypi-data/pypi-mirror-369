from abc import ABC
from typing import Callable, TypeVar, Union

from ..messages import Message

A = TypeVar("A")
B = TypeVar("B")


class Result(ABC):
    def match(
        self,
        ok: Callable[[list[dict], list[Message]], A],
        err: Callable[[list[Message], list[Message]], B],
    ) -> Union[A, B]: ...


class Ok(Result):
    __match_args__ = ("value", "warnings")

    def __init__(self, value: list[dict], warnings: list[Message]):
        self.value = value
        self.warnings = warnings

    def match(
        self,
        ok: Callable[[list[dict], list[Message]], A],
        err: Callable[[list[Message], list[Message]], B],
    ) -> Union[A, B]:
        return ok(self.value, self.warnings)


class Err(Result):
    __match_args__ = ("errors", "warnings")

    def __init__(self, errors: list[Message], warnings: list[Message]):
        self.errors = errors
        self.warnings = warnings

    def match(
        self,
        ok: Callable[[list[dict], list[Message]], A],
        err: Callable[[list[Message], list[Message]], B],
    ) -> Union[A, B]:
        return err(self.errors, self.warnings)
