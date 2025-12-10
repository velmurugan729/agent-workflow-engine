from fastapi import FastAPI, HTTPException
from typing import List

from .models import (
    GraphCreateRequest,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
    ExecutionStep,
    RunStateResponse,
    Edge,
    Node,
    Condition,
)
from .engine import create_graph, run_graph
from .storage import RUNS
from .tools import TOOLS  # ensures tools are registered


app = FastAPI(title="Minimal Agent Workflow Engine")


# ---------------------------------------------------
# 1) CREATE GRAPH
# ---------------------------------------------------
@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph_endpoint(req: GraphCreateRequest):
    graph_id = create_graph(req)
    return GraphCreateResponse(graph_id=graph_id)


# ---------------------------------------------------
# 2) RUN GRAPH
# ---------------------------------------------------
@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph_endpoint(req: GraphRunRequest):
    try:
        run_id = run_graph(req.graph_id, req.initial_state)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    run = RUNS[run_id]

    log_steps: List[ExecutionStep] = [
        ExecutionStep(node_id=step["node_id"], state_snapshot=step["state_snapshot"])
        for step in run.log
    ]

    return GraphRunResponse(
        run_id=run_id,
        final_state=run.state,
        log=log_steps,
    )


# ---------------------------------------------------
# 3) GET RUN STATE
# ---------------------------------------------------
@app.get("/graph/state/{run_id}", response_model=RunStateResponse)
async def get_run_state(run_id: str):
    if run_id not in RUNS:
        raise HTTPException(status_code=404, detail="Run not found")

    run = RUNS[run_id]
    return RunStateResponse(
        run_id=run.run_id,
        current_state=run.state,
        status=run.status.value,
        last_error=run.last_error,
    )


# ---------------------------------------------------
# 4) CREATE SAMPLE SUMMARIZATION WORKFLOW
# ---------------------------------------------------
@app.post("/graph/create/sample/summarization", response_model=GraphCreateResponse)
async def create_sample_summarization_graph():
    """
    Creates a sample workflow implementing:
      1. split_text
      2. generate_summaries
      3. merge_summaries
      4. refine_summary
    """

    nodes = [
        Node(id="split", tool_name="split_text"),
        Node(id="summarize_chunks", tool_name="generate_summaries"),
        Node(id="merge", tool_name="merge_summaries"),
        Node(id="refine", tool_name="refine_summary"),
    ]

    edges = [
        Edge(source="split", target="summarize_chunks"),
        Edge(source="summarize_chunks", target="merge"),
        Edge(source="merge", target="refine"),
    ]

    req = GraphCreateRequest(
        nodes=nodes,
        edges=edges,
        start_node_id="split",
    )

    graph_id = create_graph(req)
    return GraphCreateResponse(graph_id=graph_id)
