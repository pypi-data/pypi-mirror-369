from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ItemsSpec:
    type: str
    enum: Optional[List[str]] = None


@dataclass
class PropertyDetails:
    type: str
    description: str | None = None
    enum: Optional[List[str]] = None
    items: Optional[ItemsSpec] = None


@dataclass
class ParameterDefinition:
    type: str
    properties: Dict[str, PropertyDetails] = field(default_factory=dict)
    required: Optional[List[str]] = None


@dataclass
class FunctionToolSpec:
    name: str
    description: str
    parameters: ParameterDefinition


@dataclass
class ToolDefinition:
    type: str
    function: FunctionToolSpec


@dataclass
class NodeField:
    id: str
    name: str
    type: str
    ui_type: str
    value: Any | None = None
    default_value: Any | None = None
    validation: Optional[Dict[str, Any]] = None


@dataclass
class NodeData:
    connected_inputs: Dict[str, bool]
    workflow_name: str
    description: str
    function: Dict[str, Any]
    inputs: List[NodeField]
    label: str
    outputs: List[NodeField]
    tool: Optional[ToolDefinition] = None


@dataclass
class Position:
    x: float
    y: float


@dataclass
class Node:
    id: str
    type: str
    position: Position
    data: NodeData
    dragging: Optional[bool] = None
    height: Optional[int] = None
    position_absolute: Optional[Position] = None
    selected: Optional[bool] = None
    width: Optional[int] = None


@dataclass
class Edge:
    id: str
    source: str
    source_handle: str
    target: str
    target_handle: str


@dataclass
class Metadata:
    workflow_name: str


@dataclass
class Workflow:
    edges: List[Edge]
    nodes: List[Node]
    name: str | None = None
    metadata: Metadata | None = None
