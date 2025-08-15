from __future__ import annotations

import random
from dataclasses import dataclass

from haja_workers.function import Function


@dataclass
class RandomOutputInputs:
    text: str


@dataclass
class RandomOutputOutputs:
    output: str


def random_output_function() -> Function[RandomOutputInputs, RandomOutputOutputs]:
    fn = Function[RandomOutputInputs, RandomOutputOutputs](
        name="random_output",
        version="1.0.0",
        description="Takes input text and appends a random digit 0-9 to test caching behavior.",
    )

    async def handler(inputs: RandomOutputInputs, _event, _gs) -> RandomOutputOutputs:
        random_digit = random.randint(0, 9)
        result = f"{inputs.text}{random_digit}"
        return RandomOutputOutputs(output=result)

    return fn.with_handler(handler).with_cache_ttl(1)  # 1 second TTL for testing
