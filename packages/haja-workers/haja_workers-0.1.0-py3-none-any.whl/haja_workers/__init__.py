"""Haja Workers SDK - Python implementation for Haja Workflows.

This package provides the core functionality for building and running
workflow functions in Python.
"""

__version__ = "0.1.0"

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
