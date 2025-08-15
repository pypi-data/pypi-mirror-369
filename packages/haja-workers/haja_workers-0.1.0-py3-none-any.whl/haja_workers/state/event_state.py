from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EventState:
    server: str
    function: str
    version: str
    node: str
    workflow: str
    run: str
    function_server: str
    correlation_id: str
