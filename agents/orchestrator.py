"""
Orchestrator / Planner Agent

Uses an LLM to decompose the user's research query into a structured plan
that specifies which sub-agents should be invoked and with what parameters.
"""

import json
import logging

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

import config

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """You are a Market Research Planner. Your job is to analyse
the user's research query and produce a structured execution plan.

You MUST respond with a valid JSON object (no markdown fences) like this:

{
  "goal": "Brief summary of what the user wants",
  "use_pdf_agent": true/false,
  "pdf_instructions": "What to look for in the uploaded PDFs (or empty string)",
  "use_search_agent": true/false,
  "search_queries": ["query1", "query2"],
  "writer_instructions": "Special formatting or focus instructions for the report"
}

Rules:
- Set use_pdf_agent to true ONLY if the user has uploaded PDF files.
- Set use_search_agent to true when the query would benefit from current web data.
- Generate up to 3 focused search queries that cover different angles of the topic.
- Keep instructions concise and actionable.
"""


def planner_node(state: dict) -> dict:
    """
    LangGraph node: analyse the query and produce an execution plan.

    Reads: query, uploaded_files
    Writes: plan, status
    """
    query = state.get("query", "")
    uploaded_files = state.get("uploaded_files", [])

    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        temperature=config.LLM_TEMPERATURE,
        api_key=config.OPENAI_API_KEY,
    )

    user_content = f"Research query: {query}\n\n"
    if uploaded_files:
        file_names = [f["name"] for f in uploaded_files]
        user_content += f"Uploaded PDF files: {', '.join(file_names)}\n"
    else:
        user_content += "No PDF files uploaded.\n"

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)

    # Parse the JSON plan
    try:
        plan = json.loads(response.content.strip())
    except json.JSONDecodeError:
        # Fallback: try to extract JSON from markdown fences
        text = response.content.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        try:
            plan = json.loads(text)
        except json.JSONDecodeError:
            logger.error("Planner returned invalid JSON: %s", response.content)
            plan = {
                "goal": query,
                "use_pdf_agent": bool(uploaded_files),
                "pdf_instructions": "Extract all relevant content",
                "use_search_agent": True,
                "search_queries": [query],
                "writer_instructions": "Write a comprehensive financial analysis",
            }

    # If no PDFs uploaded, never use pdf agent
    if not uploaded_files:
        plan["use_pdf_agent"] = False

    logger.info("Plan: %s", plan)

    return {
        "plan": plan,
        "status": {"planner": "✅ Plan created"},
    }
