from __future__ import annotations

import asyncio
import json
from typing import Any

from haja_workers.state.event_state import EventState
from haja_workers.state.global_state import GlobalState
from haja_workers.types import events as ev
from haja_workers.types.keys import function_key
from haja_workers.types.message import EventMessage


async def handle_incoming_workflow(gs: GlobalState) -> None:
    dispatcher = gs.dispatcher

    def _register_handlers() -> None:
        async def on_function_request(message: EventMessage) -> None:
            fs = EventState(
                server=message.server,
                function=message.function,
                version=message.version,
                node=message.node,
                workflow=message.workflow,
                run=message.run,
                function_server=gs.server_name,
                correlation_id=message.correlation_id,
            )
            function_key_str = function_key(fs.function_server, fs.function, fs.version)
            function = gs.functions.get(function_key_str)
            if function is None:
                await _send_error_event(gs, fs, "Function not found")
                return
            outputs = await function.execute(message.payload, message)
            await _send_function_response(gs, fs, outputs)

        async def on_function_response(message: EventMessage) -> None:
            if gs.rpc_client is not None:
                gs.rpc_client.handle_call_response(message)

        async def on_cache_response(message: EventMessage) -> None:
            if gs.grpc_cache is not None:
                gs.grpc_cache.handle_response(message)

        async def on_store_response(message: EventMessage) -> None:
            if gs.grpc_store is not None:
                gs.grpc_store.handle_response(message)

        async def on_request_list_functions(message: EventMessage) -> None:
            fs = EventState(
                server=message.server,
                function=message.function,
                version=message.version,
                node=message.node,
                workflow=message.workflow,
                run=message.run,
                function_server=gs.server_name,
                correlation_id=message.correlation_id,
            )
            await handle_list_functions(gs, fs)

        async def on_request_server_name(message: EventMessage) -> None:
            fs = EventState(
                server=message.server,
                function=message.function,
                version=message.version,
                node=message.node,
                workflow=message.workflow,
                run=message.run,
                function_server=gs.server_name,
                correlation_id=message.correlation_id,
            )
            await _handle_server_name(gs, fs)

        async def on_request_server_info(message: EventMessage) -> None:
            fs = EventState(
                server=message.server,
                function=message.function,
                version=message.version,
                node=message.node,
                workflow=message.workflow,
                run=message.run,
                function_server=gs.server_name,
                correlation_id=message.correlation_id,
            )
            await _handle_server_name(gs, fs)
            await handle_list_functions(gs, fs)

        # Register
        dispatcher.register(ev.EventFunctionRequest, lambda m: asyncio.create_task(on_function_request(m)))
        dispatcher.register(ev.EventFunctionResponse, lambda m: asyncio.create_task(on_function_response(m)))
        dispatcher.register(ev.EventCacheGetResponse, lambda m: asyncio.create_task(on_cache_response(m)))
        dispatcher.register(ev.EventCacheSetResponse, lambda m: asyncio.create_task(on_cache_response(m)))
        dispatcher.register(ev.EventStoreGetResponse, lambda m: asyncio.create_task(on_store_response(m)))
        dispatcher.register(ev.EventStoreSetResponse, lambda m: asyncio.create_task(on_store_response(m)))
        dispatcher.register(ev.EventRequestListFunctions, lambda m: asyncio.create_task(on_request_list_functions(m)))
        dispatcher.register(ev.EventRequestServerName, lambda m: asyncio.create_task(on_request_server_name(m)))
        dispatcher.register(ev.EventRequestServerInfo, lambda m: asyncio.create_task(on_request_server_info(m)))

    _register_handlers()

    async for msg in gs.workflow_comm.receive_events():
        if (
            msg.workflow == ""
            and msg.event
            not in {
                ev.EventCacheGetResponse,
                ev.EventCacheSetResponse,
                ev.EventStoreGetResponse,
                ev.EventStoreSetResponse,
                ev.EventRequestServerInfo,
                ev.EventRequestServerName,
                ev.EventRequestListFunctions,
            }
        ):
            continue
        await dispatcher.dispatch(msg)


async def _send_error_event(gs: GlobalState, fs: EventState, error_text: str) -> None:
    event = EventMessage(
        function=fs.function,
        version=fs.version,
        node=fs.node,
        workflow=fs.workflow,
        run=fs.run,
        event=ev.EventError,
        text=error_text,
        correlation_id=fs.correlation_id,
    )
    await gs.workflow_comm.send_event(event)


async def _send_function_response(gs: GlobalState, fs: EventState, payload: bytes | None) -> None:
    event = EventMessage(
        function=fs.function,
        version=fs.version,
        node=fs.node,
        workflow=fs.workflow,
        run=fs.run,
        event=ev.EventFunctionResponse,
        payload=payload,
        correlation_id=fs.correlation_id,
    )
    await gs.workflow_comm.send_event(event)


async def handle_list_functions(gs: GlobalState, fs: EventState) -> None:
    functions: list[dict[str, Any]] = []
    for _, value in gs.functions.items():
        try:
            definition = value.get_function_definition()
            # Inject server name so clients can attribute the function correctly
            definition["server"] = gs.server_name
            functions.append(definition)
        except Exception:
            continue
    payload_bytes = json.dumps(functions).encode("utf-8")
    event = EventMessage(
        function=fs.function,
        version=fs.version,
        node=fs.node,
        workflow=fs.workflow,
        run=fs.run,
        server=gs.server_name,
        event=ev.EventResponseListFunctions,
        text="List of functions",
        payload=payload_bytes,
        correlation_id=fs.correlation_id,
    )
    await gs.workflow_comm.send_event(event)


async def _handle_server_name(gs: GlobalState, fs: EventState) -> None:
    event = EventMessage(
        function=fs.function,
        version=fs.version,
        node=fs.node,
        workflow=fs.workflow,
        run=fs.run,
        server=gs.server_name,
        event=ev.EventResponseServerName,
        text=gs.server_name,
        correlation_id=fs.correlation_id,
    )
    await gs.workflow_comm.send_event(event)
