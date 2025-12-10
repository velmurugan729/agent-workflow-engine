from typing import Callable, Dict, Any, List

ToolFunc = Callable[[Dict[str, Any]], Dict[str, Any]]

TOOLS: Dict[str, ToolFunc] = {}


def register_tool(name: str):
    """Decorator to register a function as a tool."""
    def decorator(func: ToolFunc) -> ToolFunc:
        TOOLS[name] = func
        return func
    return decorator


def get_tool(name: str) -> ToolFunc:
    if name not in TOOLS:
        raise ValueError(f"Tool '{name}' is not registered")
    return TOOLS[name]


# ------------------------
# Example workflow: Summarization + Refinement
# ------------------------

@register_tool("split_text")
def split_text_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input:
      state["text"]: full input text
      state["chunk_size"]: (optional) max chars per chunk, default 300
    Output:
      state["chunks"]: List[str]
    """
    text = state.get("text", "")
    chunk_size = int(state.get("chunk_size", 300))

    chunks: List[str] = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i: i + chunk_size])

    state["chunks"] = chunks
    return state


@register_tool("generate_summaries")
def generate_summaries_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input:
      state["chunks"]: List[str]
    Output:
      state["summaries"]: List[str]
    Simple heuristic: take first ~100 characters of each chunk.
    """
    chunks: List[str] = state.get("chunks", [])
    summaries = [chunk[:100].strip() for chunk in chunks]
    state["summaries"] = summaries
    return state


@register_tool("merge_summaries")
def merge_summaries_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input:
      state["summaries"]: List[str]
    Output:
      state["summary"]: str
    """
    summaries: List[str] = state.get("summaries", [])
    merged = " ".join(summaries)
    state["summary"] = merged
    return state


@register_tool("refine_summary")
def refine_summary_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input:
      state["summary"]: current summary
      state["max_summary_length"]: target max length (int)
    Output:
      state["summary"]: refined/shortened summary
    Simple heuristic: if too long, keep only first N characters.
    """
    summary: str = state.get("summary", "")
    max_len = int(state.get("max_summary_length", 400))

    if len(summary) > max_len:
        summary = summary[:max_len].rsplit(" ", 1)[0]  # cut on word boundary

    state["summary"] = summary
    return state
