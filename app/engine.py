import uuid
from typing import Dict, Any, List, Optional

from .models import Condition, Edge, GraphCreateRequest
from .storage import GRAPHS, RUNS, StoredGraph, RunRecord, RunStatus
from .tools import get_tool


def _evaluate_condition(condition: Condition, state: Dict[str, Any]) -> bool:
    """Evaluate a condition against the current state."""
    value = state.get(condition.key)

    # Length-based operators
    if condition.op.startswith("length_"):
        if value is None:
            return False
        length = len(str(value))
        cmp_val = int(condition.value)
        if condition.op == "length_lt":
            return length < cmp_val
        if condition.op == "length_lte":
            return length <= cmp_val
        if condition.op == "length_gt":
            return length > cmp_val
        if condition.op == "length_gte":
            return length >= cmp_val
        return False

    # Standard comparison operators
    cmp_val = condition.value
    try:
        if condition.op == "lt":
            return value < cmp_val
        if condition.op == "lte":
            return value <= cmp_val
        if condition.op == "gt":
            return value > cmp_val
        if condition.op == "gte":
            return value >= cmp_val
        if condition.op == "eq":
            return value == cmp_val
        if condition.op == "ne":
            return value != cmp_val
    except TypeError:
        # If types can't be compared, treat as False
        return False

    return False


def create_graph(req: GraphCreateRequest) -> str:
    """Store a new graph definition and return its id."""
    graph_id = str(uuid.uuid4())

    nodes_map: Dict[str, str] = {n.id: n.tool_name for n in req.nodes}

    edges_map: Dict[str, List[dict]] = {}
    for edge in req.edges:
        edges_map.setdefault(edge.source, []).append(edge.dict())

    stored = StoredGraph(
        graph_id=graph_id,
        start_node_id=req.start_node_id,
        nodes=nodes_map,
        edges=edges_map,
    )
    GRAPHS[graph_id] = stored
    return graph_id


def run_graph(graph_id: str, initial_state: Dict[str, Any]) -> str:
    """Execute the graph synchronously, updating shared state."""
    if graph_id not in GRAPHS:
        raise ValueError("Graph not found")

    graph = GRAPHS[graph_id]
    run_id = str(uuid.uuid4())

    run = RunRecord(
        run_id=run_id,
        graph_id=graph_id,
        status=RunStatus.RUNNING,
        state=dict(initial_state),
        log=[],
    )
    RUNS[run_id] = run

    try:
        current_node_id: Optional[str] = graph.start_node_id

        while current_node_id is not None:
            # Log state before executing this node
            run.log.append(
                {
                    "node_id": current_node_id,
                    "state_snapshot": dict(run.state),
                }
            )

            # Get tool name for this node
            tool_name = graph.nodes[current_node_id]
            tool = get_tool(tool_name)

            # Execute tool and update state
            run.state = tool(run.state)

            # Decide next node based on edges and conditions
            next_node_id: Optional[str] = None
            for edge_dict in graph.edges.get(current_node_id, []):
                edge = Edge(**edge_dict)
                if edge.condition is None or _evaluate_condition(edge.condition, run.state):
                    next_node_id = edge.target
                    break

            current_node_id = next_node_id

        run.status = RunStatus.COMPLETED
    except Exception as e:
        run.status = RunStatus.FAILED
        run.last_error = str(e)

    return run_id
