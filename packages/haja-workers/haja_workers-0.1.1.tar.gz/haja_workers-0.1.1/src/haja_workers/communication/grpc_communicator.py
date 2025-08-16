from __future__ import annotations

import asyncio
import contextlib
import logging
from dataclasses import dataclass
from typing import AsyncIterator, Optional, TYPE_CHECKING

import grpc
from grpc import StatusCode

from haja_workers.types.message import EventMessage
from haja_workers.types import events as ev
from haja_workers.workflowsgrpc.converters import convert_from_grpc, convert_to_grpc


logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # Only imported for static type checking
    from haja_workers.workflowsgrpc.events_pb2_grpc import EventServiceStub


@dataclass
class CommunicatorConfig:
    address: str
    server_name: str
    server_api_token: str = ""
    reconnect_delay_seconds: float = 5.0
    health_interval_seconds: float = 30.0
    outgoing_queue_size: int = 1000
    ready_timeout_seconds: float = 3.0


class GrpcCommunicator:
    def __init__(self, config: CommunicatorConfig) -> None:
        self._config = config
        self._channel: Optional[grpc.aio.Channel] = None
        self._stub: Optional["EventServiceStub"] = None
        self._stream: Optional[AsyncIterator[object]] = None
        self._connected_event = asyncio.Event()
        self._closed = False
        self._outgoing: asyncio.Queue[EventMessage] = asyncio.Queue(maxsize=config.outgoing_queue_size)
        self._incoming: asyncio.Queue[EventMessage] = asyncio.Queue(maxsize=config.outgoing_queue_size)
        self._tasks: set[asyncio.Task] = set()

    async def start(self) -> None:
        self._closed = False
        task = asyncio.create_task(self._run())
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def close(self) -> None:
        logger.info("GrpcCommunicator: closing")
        self._closed = True
        if self._channel is not None:
            await self._channel.close()
        for t in list(self._tasks):
            t.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.gather(*self._tasks)
        self._connected_event.clear()

    def is_connected(self) -> bool:
        return self._connected_event.is_set()

    async def send_event(self, event: EventMessage) -> None:
        await self._outgoing.put(event)

    async def receive_events(self) -> AsyncIterator[EventMessage]:
        while not self._closed:
            msg = await self._incoming.get()
            yield msg

    async def _run(self) -> None:
        from haja_workers.workflowsgrpc import events_pb2_grpc  # type: ignore

        while not self._closed:
            try:
                logger.info("GrpcCommunicator: connecting to %s", self._config.address)
                
                # Warn if no API token is provided
                if not self._config.server_api_token:
                    logger.warning("⚠️  Warning: No API token provided. Set SERVER_API_TOKEN environment variable for authentication.")
                
                self._channel = grpc.aio.insecure_channel(self._config.address)
                # Wait briefly for channel readiness to surface connection attempts in logs
                try:
                    await asyncio.wait_for(self._channel.channel_ready(), timeout=self._config.ready_timeout_seconds)
                    logger.info("GrpcCommunicator: channel ready")
                except asyncio.TimeoutError:
                    logger.warning("GrpcCommunicator: channel not ready within %.1fs (will proceed)", self._config.ready_timeout_seconds)
                self._stub = events_pb2_grpc.EventServiceStub(self._channel)
                assert self._stub is not None
                
                # Create metadata with authentication token if provided
                metadata = []
                if self._config.server_api_token:
                    metadata.append(("authorization", f"Bearer {self._config.server_api_token}"))
                
                self._stream = self._stub.Events(self._event_generator(), metadata=metadata)
                logger.info("GrpcCommunicator: connected; starting receiver loop")
                self._connected_event.set()
                
                # Send initial registration message
                registration_msg = EventMessage(
                    server=self._config.server_name,
                    event=ev.EventResponseServerName,
                    text="Client registration",
                    correlation_id="",
                )
                await self._outgoing.put(registration_msg)
                
                receiver = asyncio.create_task(self._receiver_loop())
                self._tasks.add(receiver)
                receiver.add_done_callback(self._tasks.discard)
                await receiver
            except Exception as exc:
                # Check if this is an authentication error
                if isinstance(exc, grpc.aio.AioRpcError) and exc.code() == StatusCode.UNAUTHENTICATED:
                    if not self._config.server_api_token:
                        logger.error("❌ Authentication failed: No API token provided. Set SERVER_API_TOKEN environment variable.")
                    else:
                        logger.error("❌ Authentication failed: Invalid or expired API token. Error: %s", exc.details())
                else:
                    logger.warning("GrpcCommunicator: stream closed or error: %s", exc)
                self._connected_event.clear()
                await asyncio.sleep(self._config.reconnect_delay_seconds)

    async def _event_generator(self):
        while not self._closed:
            event = await self._outgoing.get()
            yield convert_to_grpc(event)

    async def _receiver_loop(self):
        try:
            async for in_msg in self._stream:  # type: ignore[attr-defined]
                await self._incoming.put(convert_from_grpc(in_msg))
        except grpc.aio.AioRpcError as exc:
            if exc.code() == StatusCode.UNAUTHENTICATED:
                if not self._config.server_api_token:
                    logger.error("❌ Authentication failed during message reception: No API token provided. Set SERVER_API_TOKEN environment variable.")
                else:
                    logger.error("❌ Authentication failed during message reception: Invalid or expired API token. Error: %s", exc.details())
            raise  # Re-raise to be handled by the outer exception handler
