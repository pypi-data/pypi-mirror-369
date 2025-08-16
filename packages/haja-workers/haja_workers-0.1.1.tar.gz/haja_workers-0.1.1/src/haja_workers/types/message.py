from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class EventMessage:
    """Event message containing workflow context and metadata.
    
    EventMessage is passed to function handlers as the second parameter,
    providing access to workflow context, event metadata, and correlation
    information.
    
    Attributes:
        function: Name of the function being invoked
        node: Workflow node identifier  
        workflow: Workflow identifier
        version: Function version being invoked
        server: Server that should handle this function
        event: Type of event (e.g., "function_request")
        text: Human-readable event description
        run: Workflow run identifier
        meta: Additional metadata as key-value pairs
        payload: Raw payload bytes (usually handled automatically)
        correlation_id: Unique identifier for request tracking
        
    Example:
        Function handlers receive this as the second parameter:
        >>> async def my_handler(inputs: MyInput, event: EventMessage, gs) -> MyOutput:
        ...     print(f"Processing {event.function} in workflow {event.workflow}")
        ...     print(f"Run ID: {event.run}, Node: {event.node}")
        ...     return MyOutput(...)
    """
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
