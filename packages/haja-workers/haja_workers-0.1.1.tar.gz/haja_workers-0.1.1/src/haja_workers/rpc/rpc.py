from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Optional

from haja_workers.correlation.router import Router
from haja_workers.types import events as ev
from haja_workers.types.message import EventMessage


@dataclass
class RpcClient:
    communicator: Any
    router: Router

    @classmethod
    def new_with_communicator(cls, communicator: Any) -> "RpcClient":
        return cls(communicator=communicator, router=Router())

    async def send_status_event(self, event_state: EventMessage, text: str, payload: Any | None = None) -> None:
        if event_state is None:
            raise ValueError("event_state is None")
        payload_bytes = None
        if payload is not None:
            payload_bytes = json.dumps(payload).encode("utf-8")
        status_msg = EventMessage(
            function=event_state.function,
            version=event_state.version,
            node=event_state.node,
            workflow=event_state.workflow,
            run=event_state.run,
            server=event_state.server,
            event=ev.EventStatusMessage,
            text=text,
            payload=payload_bytes,
            correlation_id=event_state.correlation_id,
        )
        await self.communicator.send_event(status_msg)

    async def call(self, timeout_minutes: int, execution_node: Any, event_state: EventMessage, payload: Any) -> bytes:
        payload_bytes = json.dumps(payload).encode("utf-8")
        loop = asyncio.get_running_loop()
        correlation_id = getattr(event_state, "correlation_id", None) or ""
        # generate new correlation id for the call
        import uuid

        correlation_id = uuid.uuid4().hex
        fut = self.router.register(correlation_id)

        if execution_node.type != "flow_tool":
            event_msg = EventMessage(
                function=execution_node.data["function"]["name"],
                version=execution_node.data["function"]["version"],
                server=execution_node.data["function"]["server"],
                node=execution_node.id,
                workflow=event_state.workflow,
                run=event_state.run,
                event=ev.eventFunctionRequest,
                text=f"Node {execution_node.id} is invoking a function from a tool server",
                meta={"calling_server": event_state.server},
                payload=payload_bytes,
                correlation_id=correlation_id,
            )
        else:
            event_msg = EventMessage(
                server=event_state.server,
                node=execution_node.id,
                workflow=event_state.workflow,
                run=event_state.run,
                event=ev.eventFlowNodeRequest,
                text=f"Node {execution_node.id} is invoking a flow from a tool server",
                payload=payload_bytes,
                correlation_id=correlation_id,
            )
        await self.communicator.send_event(event_msg)

        try:
            response: EventMessage = await asyncio.wait_for(
                fut, timeout=timeout_minutes * 60
            )
        except asyncio.TimeoutError as e:
            raise e
        if response.payload is None:
            raise ValueError("received empty payload")
        return response.payload

    def handle_call_response(self, response: EventMessage) -> None:
        if response.event != ev.eventFunctionResponse:
            return
        self.router.deliver(response.correlation_id, response)
