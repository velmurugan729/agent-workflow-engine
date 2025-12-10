A clean, minimal implementation of a workflow/graph engine using FastAPI.
The engine supports sequential node execution, state transitions, conditional branching, looping, and an example summarization workflow.

This project is built according to the assignment requirements for the AI Engineering Internship.

🚀 How to Run
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Start the FastAPI server
python -m uvicorn app.main:app --reload

3️⃣ Open Swagger UI
http://127.0.0.1:8000/docs


From here you can:

Create graphs

Run workflows

Inspect run state

Test the sample summarization pipeline

🧠 What My Workflow Engine Supports

This project implements a simple but complete graph-based workflow engine with the following capabilities:

✔️ Nodes (Tools)

Each node is a registered Python function that:

Reads the shared state

Updates it

Returns the modified state

Tools implemented:

split_text

generate_summaries

merge_summaries

refine_summary

✔️ Shared State Passing

The core of the engine is a shared Python dictionary.
Each node receives this state, mutates it, and passes it forward.

✔️ Edges & Transitions

Edges define which node comes next.
Each edge may contain a condition, enabling:

Conditional branching

Dynamic routing

Optional looping (edge back to same node)

✔️ Looping

If an edge points backward and the condition remains true, the node re-executes.

✔️ Execution Log

At every node, the engine records:

Node executed

Snapshot of state before execution

The final API response includes this complete log for transparency.

✔️ Example Workflow Included (Summarization Pipeline)

The sample workflow demonstrates a full pipeline:

Split text into chunks

Summarize each chunk

Merge summaries

Refine the final summary

This shows linear workflow + optional iterative refinement.

🔧 What I Would Improve With More Time

These enhancements would move the project closer to production-quality workflow engines:

⭐ 1. Persistent Storage

Use SQLite/Postgres to store graphs and runs instead of in-memory dictionaries.

⭐ 2. WebSocket Log Streaming

Provide real-time node-by-node updates to a UI.

⭐ 3. Async Execution

Support long-running tasks using async workflows.

⭐ 4. Graph Validation

Detect:

Cycles

Unreachable nodes

Missing tool names

Invalid transitions

⭐ 5. Visual Workflow Builder

A small frontend to design graphs by dragging nodes and edges.

⭐ 6. Dynamic Tool Loading

Allow adding new tools via API rather than hardcoding them.

These improvements would bring the system closer to tools like LangGraph, CrewAI flow engines, or Airflow DAGs.

🔁 Workflow Diagram
ASCII Diagram (Viva-Friendly)
 ┌──────────────┐
 │  split_text   │
 └───────┬──────┘
         ▼
 ┌──────────────┐
 │ summarize     │
 │   chunks      │
 └───────┬──────┘
         ▼
 ┌──────────────┐
 │ merge         │
 │ summaries     │
 └───────┬──────┘
         ▼
 ┌──────────────┐
 │ refine        │
 │ summary       │
 └───────┬──────┘
         ▼
        End

Mermaid Diagram (GitHub Rendered)
flowchart TD

A[Split Text] --> B[Generate Summaries]
B --> C[Merge Summaries]
C --> D[Refine Summary]

%% Optional loop
D -->|If too long| D

📂 Project Structure
your-repo/
├── app/
│   ├── main.py          # FastAPI routes
│   ├── models.py        # Pydantic schemas
│   ├── engine.py        # Workflow engine logic
│   ├── tools.py         # Node tools + registry
│   └── storage.py       # In-memory store
├── requirements.txt
└── README.md

🌐 API Overview
POST /graph/create

Create a workflow graph.

POST /graph/run

Execute the graph with initial state → returns:

final state

run_id

execution log

GET /graph/state/{run_id}

Inspect the current state of a specific run.

POST /graph/create/sample/summarization

Quickly generate the summarization pipeline.
