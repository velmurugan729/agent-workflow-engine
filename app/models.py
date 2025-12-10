from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel


class Condition(BaseModel):
    key: str
    op: Literal[
        "lt",
        "lte",
        "gt",
        "gte",
        "eq",
        "ne",
        "length_lt",
        "length_lte",
        "length_gt",
        "length_gte",
    ]
    value: Any


class Edge(BaseModel):
    source: str
    target: str
    condition: Optional[Condition] = None


class Node(BaseModel):
    id: str
    tool_name: str


class GraphCreateRequest(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    start_node_id: str


class GraphCreateResponse(BaseModel):
    graph_id: str


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]


class ExecutionStep(BaseModel):
    node_id: str
    state_snapshot: Dict[str, Any]


class GraphRunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    log: List[ExecutionStep]


class RunStateResponse(BaseModel):
    run_id: str
    current_state: Dict[str, Any]
    status: Literal["pending", "running", "completed", "failed"]
    last_error: Optional[str] = None
