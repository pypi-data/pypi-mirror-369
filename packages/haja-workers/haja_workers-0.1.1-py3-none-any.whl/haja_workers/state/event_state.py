from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EventState:
    """Internal event state for tracking workflow execution context.
    
    EventState is used internally by the SDK to track the state of workflow
    events and function executions. Most users won't interact with this directly,
    but it's available for advanced use cases.
    
    Attributes:
        server: Name of the workflow server
        function: Function name being executed
        version: Function version being executed
        node: Workflow node identifier
        workflow: Workflow identifier
        run: Workflow run identifier  
        function_server: Server hosting the function
        correlation_id: Unique identifier for request correlation
        
    Note:
        This class is primarily for internal SDK use. Function handlers
        receive EventMessage instead, which contains similar information
        in a more user-friendly format.
    """
    server: str
    function: str
    version: str
    node: str
    workflow: str
    run: str
    function_server: str
    correlation_id: str
