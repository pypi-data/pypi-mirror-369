from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Dict

from haja_workers.types.message import EventMessage


Handler = Callable[[EventMessage], "asyncio.Future | asyncio.Task | None"]


class Dispatcher:
    def __init__(self, queue_size: int = 1000) -> None:
        self._registry: Dict[str, Handler] = {}
        self._jobs: asyncio.Queue[EventMessage] = asyncio.Queue(maxsize=queue_size)
        self._workers: list[asyncio.Task] = []
        self._stopped = asyncio.Event()

    def register(self, event: str, handler: Handler) -> None:
        self._registry[event] = handler

    async def start(self, workers: int = 1) -> None:
        workers = max(1, workers)
        self._stopped.clear()
        for _ in range(workers):
            self._workers.append(asyncio.create_task(self._worker()))

    async def stop(self) -> None:
        self._stopped.set()
        for _ in self._workers:
            await self._jobs.put(EventMessage(event="__stop__"))
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

    async def dispatch(self, msg: EventMessage) -> None:
        await self._jobs.put(msg)

    async def _worker(self) -> None:
        while True:
            msg = await self._jobs.get()
            if msg.event == "__stop__" and self._stopped.is_set():
                break
            handler = self._registry.get(msg.event)
            if handler is not None:
                result = handler(msg)
                if asyncio.iscoroutine(result):
                    await result
