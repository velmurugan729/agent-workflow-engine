from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class StoredGraph:
    graph_id: str
    start_node_id: str
    # node_id -> tool_name
    nodes: Dict[str, str]
    # node_id -> list of edges (stored as plain dicts)
    edges: Dict[str, List[dict]]


@dataclass
class RunRecord:
    run_id: str
    graph_id: str
    status: RunStatus = RunStatus.PENDING
    state: Dict[str, Any] = field(default_factory=dict)
    log: List[Dict[str, Any]] = field(default_factory=list)
    last_error: Optional[str] = None


# In-memory "database"
GRAPHS: Dict[str, StoredGraph] = {}
RUNS: Dict[str, RunRecord] = {}
