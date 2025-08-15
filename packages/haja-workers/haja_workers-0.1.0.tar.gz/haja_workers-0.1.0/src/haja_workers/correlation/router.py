from __future__ import annotations

import asyncio
from typing import Dict, Optional

from haja_workers.types.message import EventMessage


class Router:
    def __init__(self) -> None:
        self._locks: Dict[str, asyncio.Lock] = {}
        self._futures: Dict[str, asyncio.Future[EventMessage]] = {}

    def register(self, correlation_id: str) -> asyncio.Future[EventMessage]:
        if correlation_id in self._futures:
            return self._futures[correlation_id]
        fut: asyncio.Future[EventMessage] = asyncio.get_running_loop().create_future()
        self._futures[correlation_id] = fut
        self._locks.setdefault(correlation_id, asyncio.Lock())
        return fut

    def deliver(self, correlation_id: str, message: EventMessage) -> None:
        fut = self._futures.get(correlation_id)
        if fut and not fut.done():
            fut.set_result(message)

    def remove(self, correlation_id: str) -> None:
        self._futures.pop(correlation_id, None)
        self._locks.pop(correlation_id, None)
