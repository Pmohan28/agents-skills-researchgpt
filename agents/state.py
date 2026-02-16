"""
Shared State for the LangGraph Agent Graph

Defines the TypedDict that flows through all agent nodes.
"""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State shared across all nodes in the LangGraph research pipeline."""

    # The original user query
    query: str

    # Structured plan produced by the orchestrator
    plan: dict

    # Files uploaded by the user (list of {name, bytes} dicts)
    uploaded_files: list[dict]

    # Text extracted from PDFs
    pdf_content: str

    # Web search results (list of result dicts)
    search_results: list[dict]

    # Final synthesised report
    report: str

    # Status updates for the UI  (agent_name → status string)
    status: dict

    # Chat history
    messages: Annotated[list[BaseMessage], add_messages]
