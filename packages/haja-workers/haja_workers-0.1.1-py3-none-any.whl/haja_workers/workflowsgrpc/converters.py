from __future__ import annotations

from typing import Optional

from google.protobuf.struct_pb2 import Struct

from haja_workers.types.message import EventMessage


def convert_to_grpc(in_msg: EventMessage):
    """Converts EventMessage to protobuf GrpcEventMessage.
    Imports stubs lazily to avoid hard dependency before generation.
    """
    from . import events_pb2  # type: ignore

    meta_struct: Optional[Struct] = None
    if in_msg.meta is not None:
        meta_struct = Struct()
        meta_struct.update(in_msg.meta)

    return events_pb2.GrpcEventMessage(
        function=in_msg.function,
        node=in_msg.node,
        workflow=in_msg.workflow,
        version=in_msg.version,
        server=in_msg.server,
        event=in_msg.event,
        text=in_msg.text,
        run=in_msg.run,
        meta=meta_struct,
        payload=in_msg.payload or b"",
        correlation_id=in_msg.correlation_id,
    )


def convert_from_grpc(in_msg) -> EventMessage:
    """Converts protobuf GrpcEventMessage to EventMessage."""
    meta_dict = None
    if getattr(in_msg, "meta", None) is not None:
        meta_dict = dict(in_msg.meta)
    payload = bytes(in_msg.payload) if getattr(in_msg, "payload", None) else None
    return EventMessage(
        function=in_msg.function,
        node=in_msg.node,
        workflow=in_msg.workflow,
        version=in_msg.version,
        server=in_msg.server,
        event=in_msg.event,
        text=in_msg.text,
        run=in_msg.run,
        meta=meta_dict,
        payload=payload,
        correlation_id=in_msg.correlation_id,
    )
