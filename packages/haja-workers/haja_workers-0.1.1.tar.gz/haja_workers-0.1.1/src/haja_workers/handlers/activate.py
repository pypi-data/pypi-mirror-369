from __future__ import annotations

import asyncio

from haja_workers.handlers.inbound_workflow_handler import handle_incoming_workflow
from haja_workers.state.global_state import GlobalState


async def activate(gs: GlobalState) -> None:
    # Start dispatcher workers
    await gs.dispatcher.start(workers=4)
    # Start inbound workflow reader
    asyncio.create_task(handle_incoming_workflow(gs))
