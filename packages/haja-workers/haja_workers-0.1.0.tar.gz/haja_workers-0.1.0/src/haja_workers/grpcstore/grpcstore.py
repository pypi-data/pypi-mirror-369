from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from haja_workers.correlation.router import Router
from haja_workers.types import events as ev
from haja_workers.types.message import EventMessage
from haja_workers.utils.uid import uid


@dataclass
class Client:
    communicator: Any
    server_name: str
    default_timeout_seconds: float = 30.0

    def __post_init__(self) -> None:
        self._router = Router()

    async def get(self, workflow_id: str, key: str) -> bytes:
        correlation_id = uid()
        fut = self._router.register(correlation_id)
        event = EventMessage(
            workflow=workflow_id,
            event=ev.EventStoreGetRequest,
            text="Store get request",
            meta={"Workflow": workflow_id, "Key": key, "calling_server": self.server_name},
            correlation_id=correlation_id,
        )
        await self.communicator.send_event(event)
        resp = await asyncio.wait_for(fut, timeout=self.default_timeout_seconds)
        if resp.payload is None:
            return b""  # Return empty bytes instead of raising error - this is normal for missing keys
        return resp.payload

    async def set(self, workflow_id: str, key: str, value: bytes) -> None:
        event = EventMessage(
            workflow=workflow_id,
            event=ev.EventStoreSetRequest,
            text="Store set request",
            meta={"Workflow": workflow_id, "Key": key, "calling_server": self.server_name},
            payload=bytes(value),
            correlation_id=uid(),
        )
        await self.communicator.send_event(event)

    def handle_response(self, response: EventMessage) -> None:
        if response.event not in {ev.EventStoreGetResponse, ev.EventStoreSetResponse}:
            return
        self._router.deliver(response.correlation_id, response)
