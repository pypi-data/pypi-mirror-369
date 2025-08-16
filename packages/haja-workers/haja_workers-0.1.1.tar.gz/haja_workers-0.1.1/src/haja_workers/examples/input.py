from __future__ import annotations

from dataclasses import dataclass

from haja_workers.function import Function


@dataclass
class InputFunctionInputs:
    text: str


@dataclass
class InputFunctionOutputs:
    output: str


def input_function() -> Function[InputFunctionInputs, InputFunctionOutputs]:
    fn = Function[InputFunctionInputs, InputFunctionOutputs](
        name="example_input",
        version="1.0.0",
        description="Takes an input as a text and returns the same text as output.",
    )

    async def handler(inputs: InputFunctionInputs, _event, _gs) -> InputFunctionOutputs:
        if inputs and inputs.text == "error":
            raise ValueError("test error: intentionally throwing an error")
        return InputFunctionOutputs(output=inputs.text if inputs else None)

    return fn.with_handler(handler).with_cache_ttl(0)  # Disable caching
