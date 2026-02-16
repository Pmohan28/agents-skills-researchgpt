"""
LangGraph State Graph

Wires the agent nodes into a LangGraph StateGraph with conditional routing:

  START → planner → [conditional] → pdf_agent / search_agent → aggregator → writer → END

The planner decides which sub-agents to invoke.  If both are needed, they run
sequentially (pdf first, then search) to keep state merges simple.
"""

import logging

from langgraph.graph import StateGraph, END

from agents.state import AgentState
from agents.orchestrator import planner_node
from agents.pdf_agent import pdf_agent_node
from agents.search_agent import search_agent_node
from agents.writer_agent import writer_node

logger = logging.getLogger(__name__)


def _route_after_plan(state: dict) -> str:
    """Decide which agent to invoke first based on the plan."""
    plan = state.get("plan", {})
    if plan.get("use_pdf_agent"):
        return "pdf_agent"
    elif plan.get("use_search_agent"):
        return "search_agent"
    else:
        return "writer"


def _route_after_pdf(state: dict) -> str:
    """After PDF extraction, go to search if needed, otherwise to writer."""
    plan = state.get("plan", {})
    if plan.get("use_search_agent"):
        return "search_agent"
    return "writer"


def build_research_graph() -> StateGraph:
    """
    Construct and compile the LangGraph research pipeline.

    Returns a compiled StateGraph ready for `.invoke()` or `.stream()`.
    """
    graph = StateGraph(AgentState)

    # ── Add nodes ─────────────────────────────────────────────────────────
    graph.add_node("planner", planner_node)
    graph.add_node("pdf_agent", pdf_agent_node)
    graph.add_node("search_agent", search_agent_node)
    graph.add_node("writer", writer_node)

    # ── Entry point ───────────────────────────────────────────────────────
    graph.set_entry_point("planner")

    # ── Conditional edges after planner ───────────────────────────────────
    graph.add_conditional_edges(
        "planner",
        _route_after_plan,
        {
            "pdf_agent": "pdf_agent",
            "search_agent": "search_agent",
            "writer": "writer",
        },
    )

    # ── Conditional edges after PDF agent ─────────────────────────────────
    graph.add_conditional_edges(
        "pdf_agent",
        _route_after_pdf,
        {
            "search_agent": "search_agent",
            "writer": "writer",
        },
    )

    # ── Search agent always goes to writer ────────────────────────────────
    graph.add_edge("search_agent", "writer")

    # ── Writer goes to END ────────────────────────────────────────────────
    graph.add_edge("writer", END)

    return graph.compile()


# Pre-built graph instance
research_graph = build_research_graph()
