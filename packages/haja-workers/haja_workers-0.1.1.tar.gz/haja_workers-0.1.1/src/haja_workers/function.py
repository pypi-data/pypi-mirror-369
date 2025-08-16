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
    """Base interface for all workflow functions.
    
    This is the abstract base class that all function implementations must
    inherit from. It defines the contract for function definition and execution.
    
    Most users should use Function[InT, OutT] instead of implementing this directly.
    """
    def get_function_definition(self) -> dict[str, Any]:  # pragma: no cover
        """Get the function definition metadata.
        
        Returns:
            dict: Function metadata including name, version, description, and schemas.
        """
        raise NotImplementedError

    async def execute(self, payload_bytes: bytes | None, event_message: EventMessage) -> bytes | None:  # pragma: no cover
        """Execute the function with the given input.
        
        Args:
            payload_bytes: Serialized input data
            event_message: Event context and metadata
            
        Returns:
            bytes: Serialized output data, or None if no output
        """
        raise NotImplementedError


@dataclass
class SimpleFunction(Generic[InT, OutT], FunctionInterface):
    """Simplified workflow function for basic use cases.
    
    SimpleFunction provides a streamlined interface for functions that only need
    input/output transformation without access to global state, storage, or caching.
    
    For functions that need storage, caching, or global state access, use Function instead.
    
    Type Parameters:
        InT: Input dataclass type
        OutT: Output dataclass type
        
    Args:
        name: Unique name for this function
        version: Version string (e.g., "1.0.0")
        description: Human-readable description of what this function does
        handler: Optional handler function. Use .with_handler() to set.
        
    Example:
        >>> @dataclass
        ... class MyInput:
        ...     value: str
        ... 
        >>> @dataclass
        ... class MyOutput:
        ...     result: str
        ...
        >>> fn = SimpleFunction[MyInput, MyOutput](
        ...     name="echo",
        ...     version="1.0.0",
        ...     description="Echoes the input"
        ... ).with_handler(lambda inp: MyOutput(result=inp.value))
    """
    name: str
    version: str
    description: str
    handler: Optional[Callable[[InT], Awaitable[OutT] | OutT]] = None

    def with_handler(self, handler: Callable[[InT], Awaitable[OutT] | OutT]) -> "SimpleFunction[InT, OutT]":
        """Attach a handler function to this SimpleFunction.
        
        Args:
            handler: Function that takes input of type InT and returns OutT.
                Can be sync or async.
                
        Returns:
            SimpleFunction: Self for method chaining
            
        Example:
            >>> fn = SimpleFunction[MyInput, MyOutput](...).with_handler(
            ...     lambda inp: MyOutput(result=f"Got: {inp.value}")
            ... )
        """
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
    """Full-featured workflow function with access to global state and caching.
    
    Function provides complete access to the workflow system including:
    - Global state for storage and caching operations
    - Event metadata and context
    - Per-function caching configuration
    - Full type safety with dataclass inputs/outputs
    
    This is the recommended class for production workflow functions.
    
    Type Parameters:
        InT: Input dataclass type
        OutT: Output dataclass type
        
    Args:
        name: Unique name for this function
        version: Version string (e.g., "1.0.0")  
        description: Human-readable description of what this function does
        handler: Optional handler function. Use .with_handler() to set.
        global_state: Global state object (injected by server)
        cache_ttl_seconds: Cache TTL in seconds (0 disables caching)
        
    Example:
        >>> @dataclass
        ... class UserInput:
        ...     user_id: str
        ...     message: str
        ...
        >>> @dataclass
        ... class UserOutput:
        ...     response: str
        ...     cached: bool
        ...
        >>> fn = Function[UserInput, UserOutput](
        ...     name="process_user",
        ...     version="1.0.0", 
        ...     description="Process user messages with caching"
        ... )
        ...
        >>> async def handler(inp: UserInput, event, gs) -> UserOutput:
        ...     # Access storage and cache via gs (global state)
        ...     cached_response = await gs.grpc_cache.get(f"user:{inp.user_id}")
        ...     if cached_response:
        ...         return UserOutput(response=cached_response.decode(), cached=True)
        ...     
        ...     # Process and cache result
        ...     response = f"Hello {inp.user_id}: {inp.message}"
        ...     await gs.grpc_cache.set(f"user:{inp.user_id}", response.encode(), ttl_seconds=300)
        ...     return UserOutput(response=response, cached=False)
        ...
        >>> fn = fn.with_handler(handler).with_cache_ttl(300)
    """
    name: str
    version: str
    description: str
    handler: Optional[Callable[[InT, EventMessage, Any], Awaitable[OutT] | OutT]] = None
    global_state: Any | None = None
    cache_ttl_seconds: int = 0  # 0 disables caching

    def with_handler(self, handler: Callable[[InT, EventMessage, Any], Awaitable[OutT] | OutT]) -> "Function[InT, OutT]":
        """Attach a handler function to this Function.
        
        Args:
            handler: Function that takes (inputs: InT, event: EventMessage, gs: GlobalState)
                and returns OutT. Can be sync or async. The handler receives:
                - inputs: Typed input data (your InT dataclass)
                - event: Event metadata and context
                - gs: Global state with access to storage, cache, and other services
                
        Returns:
            Function: Self for method chaining
            
        Example:
            >>> async def my_handler(inputs: MyInput, event, gs) -> MyOutput:
            ...     # Use global state for storage/cache
            ...     await gs.grpc_store.set("key", b"value")
            ...     cached = await gs.grpc_cache.get("cache_key")
            ...     return MyOutput(result="processed")
            ...
            >>> fn = Function[MyInput, MyOutput](...).with_handler(my_handler)
        """
        self.handler = handler
        return self

    def with_cache_ttl(self, ttl_seconds: int) -> "Function[InT, OutT]":
        """Set the cache TTL for this function's results.
        
        Args:
            ttl_seconds: Time-to-live in seconds for cached results.
                Set to 0 to disable caching for this function.
                
        Returns:
            Function: Self for method chaining
            
        Example:
            >>> fn = Function[MyInput, MyOutput](...).with_cache_ttl(300)  # 5 minutes
        """
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
