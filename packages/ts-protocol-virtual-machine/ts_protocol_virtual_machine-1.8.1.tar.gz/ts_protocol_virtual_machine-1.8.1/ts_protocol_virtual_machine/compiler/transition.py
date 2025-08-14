from abc import ABC
from pathlib import Path
from typing import Callable

import pythonmonkey as pm


class Transition(ABC):
    @staticmethod
    def _get_function(
        source_js_name: str, target_js_name: str
    ) -> Callable[[object], dict]:
        with open(
            Path(__file__).parent.parent.joinpath("resources", "compiler.js"), "r"
        ) as file:
            return pm.eval(
                f"""
                (program) => {{
                    {file.read()};
                    return Compiler
                        .{source_js_name}
                        .to
                        .{target_js_name}(program)
                        .match(
                            (program, warnings) => ({{program, warnings}}),
                            (error, warnings) => ({{errors: error.reasons, warnings}}),
                        );
                }}
                """
            )
