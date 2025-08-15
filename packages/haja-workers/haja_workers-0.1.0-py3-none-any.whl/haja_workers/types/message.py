from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class EventMessage:
    function: str = ""
    node: str = ""
    workflow: str = ""
    version: str = ""
    server: str = ""
    event: str = ""
    text: str = ""
    run: str = ""
    meta: Optional[Dict[str, Any]] = None
    payload: Optional[bytes] = None
    correlation_id: str = ""
