from functools import cached_property
from typing import Callable, Generic, TypeVar

from ...messages import to_messages
from ...result import Err, Ok, Result
from ..transition import Transition

T = TypeVar("T")
U = TypeVar("U")


class ToTarget(Generic[U], Transition):
    def __init__(self, source_js_name: str):
        self._source_js_name = source_js_name

    @cached_property
    def _pvm_function(self) -> Callable[[U], dict]:
        return self._get_function(self._source_js_name, "pvm")

    @cached_property
    def _protocol_v2_function(self) -> Callable[[U], dict]:
        return self._get_function(self._source_js_name, "protocolV2")

    def pvm(self, input: U) -> Result:
        return _result_from_js(self._pvm_function(input))

    def protocol_v2(self, input: U) -> Result:
        return _result_from_js(self._protocol_v2_function(input))


class Source(Generic[T]):
    to: ToTarget[T]

    def __init__(self, js_name: str):
        self.to = ToTarget(js_name)


def _result_from_js(output: dict) -> Result:
    warnings = to_messages(output.get("warnings", []))
    if "program" in output:
        program = output.get("program", [])
        return Ok(program, warnings)
    errors = to_messages(output.get("errors", []))
    return Err(errors, warnings)
