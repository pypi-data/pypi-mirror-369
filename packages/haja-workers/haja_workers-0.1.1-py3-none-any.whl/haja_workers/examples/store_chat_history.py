from __future__ import annotations

import json
from dataclasses import dataclass

from haja_workers.function import Function


@dataclass
class StoreChatHistoryInputs:
    text: str


@dataclass
class StoreChatHistoryOutputs:
    history: str


def store_chat_history_function() -> Function[StoreChatHistoryInputs, StoreChatHistoryOutputs]:
    fn = Function[StoreChatHistoryInputs, StoreChatHistoryOutputs](
        name="store_chat_history",
        version="1.0.0",
        description="Appends the input text to a per-workflow chat history stored via gRPC store and returns the full history.",
    )

    async def handler(inputs: StoreChatHistoryInputs, event, gs) -> StoreChatHistoryOutputs:
        if gs is None or getattr(gs, "grpc_store", None) is None:
            raise RuntimeError("grpc store client not available")
        workflow_id = event.workflow or "__global__"
        history_key = "chat_history"
        if inputs and inputs.text in {"clear", "clear_history"}:
            await gs.grpc_store.set(workflow_id, history_key, "".encode("utf-8"))
            return StoreChatHistoryOutputs(history="cleared")
        history = []
        data = await gs.grpc_store.get(workflow_id, history_key)
        if data:
            try:
                history = json.loads(data.decode("utf-8"))
            except Exception:
                history = []
        history.append(inputs.text if inputs else None)
        bytes_data = json.dumps(history).encode("utf-8")
        await gs.grpc_store.set(workflow_id, history_key, bytes_data)
        return StoreChatHistoryOutputs(history="\n".join([x for x in history if x is not None]))

    return fn.with_handler(handler).with_cache_ttl(0)  # Disable caching
