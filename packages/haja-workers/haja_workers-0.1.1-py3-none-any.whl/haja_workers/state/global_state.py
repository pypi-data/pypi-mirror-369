from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from haja_workers.communication.grpc_communicator import GrpcCommunicator
from haja_workers.dispatcher.dispatcher import Dispatcher
from haja_workers.rpc.rpc import RpcClient  # will add later


@dataclass
class GlobalState:
    server_name: str
    workflow_comm: GrpcCommunicator
    dispatcher: Dispatcher
    rpc_client: Optional[RpcClient] = None
    grpc_cache: Any | None = None
    grpc_store: Any | None = None
    functions: Dict[str, Any] = field(default_factory=dict)
    response_handlers: Dict[str, Any] = field(default_factory=dict)
    execution_state: Dict[str, Any] = field(default_factory=dict)
