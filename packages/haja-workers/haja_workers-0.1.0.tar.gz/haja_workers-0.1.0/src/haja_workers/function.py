from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, is_dataclass, fields, asdict
from typing import Any, Awaitable, Callable, Generic, Optional, TypeVar, get_args, get_origin, get_type_hints
import inspect

from haja_workers.types.message import EventMessage

InT = TypeVar("InT")
OutT = TypeVar("OutT")


@dataclass
class FunctionInterface:
    def get_function_definition(self) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

    async def execute(self, payload_bytes: bytes | None, event_message: EventMessage) -> bytes | None:  # pragma: no cover
        raise NotImplementedError


@dataclass
class SimpleFunction(Generic[InT, OutT], FunctionInterface):
    name: str
    version: str
    description: str
    handler: Optional[Callable[[InT], Awaitable[OutT] | OutT]] = None

    def with_handler(self, handler: Callable[[InT], Awaitable[OutT] | OutT]) -> "SimpleFunction[InT, OutT]":
        self.handler = handler
        return self

    def get_function_definition(self) -> dict[str, Any]:
        inputs_schema, outputs_schema = _introspect_handler_types_simple(self.handler)
        return {
            "name": self.name,
            "version": self.version,
            "server": "",  # injected by server
            "description": self.description,
            # Keep parameters for tool schema compatibility, but also include explicit types
            "parameters": {"type": "object", "properties": {}},
            "inputs_type": json.dumps(inputs_schema),
            "outputs_type": json.dumps(outputs_schema),
            "tags": [],
        }

    async def execute(self, payload_bytes: bytes | None, event_message: EventMessage) -> bytes | None:
        if self.handler is None:
            return None
        raw_data: Any = None
        if payload_bytes:
            raw_data = json.loads(payload_bytes.decode("utf-8"))
        inputs = _convert_inputs_for_handler_simple(self.handler, raw_data)
        result = self.handler(inputs)  # type: ignore[arg-type]
        if _is_awaitable(result):
            result = await result  # type: ignore[assignment]
        return _serialize_result_to_bytes(result)


@dataclass
class Function(Generic[InT, OutT], FunctionInterface):
    name: str
    version: str
    description: str
    handler: Optional[Callable[[InT, EventMessage, Any], Awaitable[OutT] | OutT]] = None
    global_state: Any | None = None
    cache_ttl_seconds: int = 0  # 0 disables caching

    def with_handler(self, handler: Callable[[InT, EventMessage, Any], Awaitable[OutT] | OutT]) -> "Function[InT, OutT]":
        self.handler = handler
        return self

    def with_cache_ttl(self, ttl_seconds: int) -> "Function[InT, OutT]":
        self.cache_ttl_seconds = ttl_seconds
        return self

    def get_function_definition(self) -> dict[str, Any]:
        inputs_schema, outputs_schema = _introspect_handler_types(self.handler)
        return {
            "name": self.name,
            "version": self.version,
            "server": "",
            "description": self.description,
            # Keep parameters for tool schema compatibility, but also include explicit types
            "parameters": {"type": "object", "properties": {}},
            "inputs_type": json.dumps(inputs_schema),
            "outputs_type": json.dumps(outputs_schema),
            "tags": [],
        }

    async def execute(self, payload_bytes: bytes | None, event_message: EventMessage) -> bytes | None:
        if self.handler is None:
            return None
            
        # If cache is available and TTL != 0, try to get the cached result
        cache_key = None
        if (self.global_state is not None 
            and hasattr(self.global_state, 'grpc_cache') 
            and self.global_state.grpc_cache is not None 
            and self.cache_ttl_seconds > 0):
            
            cache_key = _generate_cache_key(payload_bytes or b"", self.name, self.version)
            
            try:
                cached_result = await self.global_state.grpc_cache.get_by_string(str(cache_key))
                return cached_result
            except Exception:
                pass  # Cache miss, continue to execute
        
        raw_data: Any = None
        if payload_bytes:
            raw_data = json.loads(payload_bytes.decode("utf-8"))
        inputs = _convert_inputs_for_handler(self.handler, raw_data)
        # Pass through the injected GlobalState when available
        result = self.handler(inputs, event_message, self.global_state)
        if _is_awaitable(result):
            result = await result  # type: ignore[assignment]
        result_bytes = _serialize_result_to_bytes(result)
        
        # Cache the result if caching is enabled
        if (cache_key is not None 
            and result_bytes is not None
            and self.global_state is not None 
            and hasattr(self.global_state, 'grpc_cache') 
            and self.global_state.grpc_cache is not None):
            try:
                await self.global_state.grpc_cache.set_by_string(str(cache_key), result_bytes, self.cache_ttl_seconds)
            except Exception:
                pass  # Cache store failed, continue
        
        return result_bytes

    def set_global_state(self, gs: Any) -> None:
        self.global_state = gs


# ---- Reflection utilities ----

def _introspect_handler_types(handler: Optional[Callable[..., Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Inspect a 3-arg handler(inputs, event, gs) for input and return types.

    Returns a pair of flattened schemas for inputs and outputs, respectively.
    """
    if handler is None:
        return {}, {}
    try:
        sig = inspect.signature(handler)
        hints = get_type_hints(handler)
        # Find first positional parameter as inputs
        input_type: Any = None
        for param in sig.parameters.values():
            if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                input_type = hints.get(param.name, None)
                break
        return_type: Any = hints.get("return", None)
        return _build_flat_schema(input_type), _build_flat_schema(return_type)
    except Exception:
        return {}, {}


def _introspect_handler_types_simple(handler: Optional[Callable[..., Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Inspect a 1-arg handler(inputs) for input and return types."""
    if handler is None:
        return {}, {}
    try:
        sig = inspect.signature(handler)
        hints = get_type_hints(handler)
        input_type: Any = None
        for param in sig.parameters.values():
            if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                input_type = hints.get(param.name, None)
                break
        return_type: Any = hints.get("return", None)
        return _build_flat_schema(input_type), _build_flat_schema(return_type)
    except Exception:
        return {}, {}


def _build_flat_schema(py_type: Any) -> dict[str, Any]:
    """Build a flattened schema mapping (dot-notation) to type names, similar to Go implementation.

    Examples:
    - dataclass with fields a: str, b: list[int] -> {"a": "str", "b": "[]int"}
    - nested dataclasses will be flattened: {"parent.child": "str"}
    - typing.Dict/Any/None -> {}
    """
    result: dict[str, Any] = {}
    if py_type is None:
        return result
    origin = get_origin(py_type)
    # If plain dict or Any, we cannot introspect keys
    if py_type is Any or py_type is dict or origin is dict:
        return result
    # Dataclasses
    if is_dataclass_type(py_type):
        _add_dataclass_fields_to_schema(py_type, prefix="", out=result)
        return result
    # List/tuple/set types
    if origin in (list, tuple, set):
        args = get_args(py_type)
        elem = args[0] if args else Any
        elem_str = _type_to_string(elem)
        # Represent collection as a single entry
        result["[]"] = f"[]{elem_str}"
        return result
    # Fallback to a single type
    result["type"] = _type_to_string(py_type)
    return result


def is_dataclass_type(t: Any) -> bool:
    try:
        return is_dataclass(t)
    except Exception:
        return False


def _add_dataclass_fields_to_schema(dc_type: Any, prefix: str, out: dict[str, Any]) -> None:
    for f in fields(dc_type):
        field_type = f.type
        name = f.name
        path = f"{prefix}.{name}" if prefix else name
        origin = get_origin(field_type)
        if is_dataclass_type(field_type):
            _add_dataclass_fields_to_schema(field_type, prefix=path, out=out)
        elif origin in (list, tuple, set):
            args = get_args(field_type)
            elem = args[0] if args else Any
            out[path] = f"[]{_type_to_string(elem)}"
        elif origin is dict or field_type is dict:
            # Unknown keys/values; omit
            continue
        else:
            out[path] = _type_to_string(field_type)


def _type_to_string(t: Any) -> str:
    origin = get_origin(t)
    if t is Any:
        return "any"
    if origin is None:
        # Builtins and classes
        if hasattr(t, "__name__"):
            return t.__name__
        return str(t)
    if origin in (list, tuple, set):
        args = get_args(t)
        inner = args[0] if args else Any
        return f"[]{_type_to_string(inner)}"
    if origin is dict:
        return "dict"
    return str(origin)


def _generate_cache_key(payload: bytes, name: str, version: str) -> int:
    """Generate a cache key similar to Go's hash.Generate function."""
    hasher = hashlib.sha256()
    hasher.update(payload)
    hasher.update(name.encode('utf-8'))
    hasher.update(version.encode('utf-8'))
    # Convert to int64-like value (take first 8 bytes and convert to int)
    return int.from_bytes(hasher.digest()[:8], 'big')


def _is_awaitable(obj: Any) -> bool:
    try:
        import inspect as _inspect
        return _inspect.isawaitable(obj)
    except Exception:
        return hasattr(obj, "__await__")


def _convert_inputs_for_handler(handler: Optional[Callable[..., Any]], raw: Any) -> Any:
    """Convert input dict into the annotated type of the first positional arg, if it's a dataclass.

    Falls back to the original raw value if no conversion is possible.
    """
    if handler is None or raw is None:
        return raw
    try:
        sig = inspect.signature(handler)
        hints = get_type_hints(handler)
        for param in sig.parameters.values():
            if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                annotated = hints.get(param.name, None)
                if annotated is not None and is_dataclass_type(annotated) and isinstance(raw, dict):
                    return annotated(**raw)
                break
    except Exception:
        pass
    return raw


def _convert_inputs_for_handler_simple(handler: Optional[Callable[..., Any]], raw: Any) -> Any:
    # Same as above but for single-argument handlers
    return _convert_inputs_for_handler(handler, raw)


def _serialize_result_to_bytes(result: Any) -> bytes | None:
    if result is None:
        return None
    # Direct bytes passthrough
    if isinstance(result, (bytes, bytearray)):
        return bytes(result)
    # Dataclass -> dict
    if is_dataclass(result):
        return json.dumps(asdict(result)).encode("utf-8")
    # Objects with model_dump (e.g., Pydantic v2)
    if hasattr(result, "model_dump") and callable(getattr(result, "model_dump")):
        try:
            return json.dumps(result.model_dump()).encode("utf-8")  # type: ignore[call-arg]
        except Exception:
            pass
    # Objects with dict() method
    if hasattr(result, "dict") and callable(getattr(result, "dict")):
        try:
            return json.dumps(result.dict()).encode("utf-8")  # type: ignore[call-arg]
        except Exception:
            pass
    # Primitives, dicts, lists
    try:
        return json.dumps(result).encode("utf-8")
    except TypeError:
        # Fallback to string representation
        return json.dumps(str(result)).encode("utf-8")
