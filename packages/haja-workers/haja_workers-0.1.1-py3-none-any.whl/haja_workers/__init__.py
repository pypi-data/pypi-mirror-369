"""Haja Workers SDK - Python implementation for Haja Workflows.

This package provides the core functionality for building and running
workflow functions in Python. It includes everything needed to create
type-safe workflow functions with access to storage, caching, and the
broader Haja workflow system.

Quick Start:
    >>> from haja_workers import Server, Function, Config
    >>> from dataclasses import dataclass
    >>> 
    >>> @dataclass
    >>> class Input:
    ...     message: str
    >>> 
    >>> @dataclass
    >>> class Output:
    ...     result: str
    >>> 
    >>> async def handler(inputs: Input, event, gs) -> Output:
    ...     return Output(result=f"Processed: {inputs.message}")
    >>> 
    >>> config = Config(server_name="my-worker")
    >>> server = Server(config)
    >>> fn = Function[Input, Output]("echo", "1.0.0", "Echo function")
    >>> server.register_function(fn.with_handler(handler))
    >>> await server.start()

Main Classes:
    - Server: Main server for running workflow functions
    - Function: Full-featured function with global state access
    - SimpleFunction: Simplified function for basic use cases  
    - Config: Configuration for server connection and behavior
    
Utility Functions:
    - load_config: Load configuration from environment and .env files
    
Type Classes:
    - EventMessage: Event context passed to function handlers
    - EventState: Event state information
"""

__version__ = "0.1.1"

# Lazy imports to avoid import errors during development
def __getattr__(name):
    if name == "Server":
        from haja_workers.sdk import Server
        return Server
    elif name == "Function":
        from haja_workers.function import Function
        return Function
    elif name == "SimpleFunction":
        from haja_workers.function import SimpleFunction
        return SimpleFunction
    elif name == "FunctionInterface":
        from haja_workers.function import FunctionInterface
        return FunctionInterface
    elif name == "Config":
        from haja_workers.config import Config
        return Config
    elif name == "load_config":
        from haja_workers.config import load_config
        return load_config
    elif name == "EventMessage":
        from haja_workers.types.message import EventMessage
        return EventMessage
    elif name == "EventState":
        from haja_workers.types.events import EventState
        return EventState
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "Server",
    "Function", 
    "SimpleFunction",
    "FunctionInterface",
    "Config",
    "load_config",
    "EventMessage",
    "EventState",
]
