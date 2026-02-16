"""
Financial Writer Agent

Synthesises research findings (PDF extracts + web search results) into
a professional, financial-language report.

Follows the Financial Writer SKILL.md specification.
"""

import logging

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

import config

logger = logging.getLogger(__name__)

WRITER_SYSTEM_PROMPT = """You are a Senior Financial Analyst and Report Writer.
Your task is to synthesise raw research data into a polished, professional
market research report written in **financial language**.

## Report Structure
1. **Executive Summary** — 2-3 sentence overview of the key takeaways.
2. **Key Findings** — Bullet-pointed highlights with supporting data.
3. **Market Analysis** — Detailed narrative discussion using financial terminology.
4. **Data & Metrics** — Present relevant numbers in tables where appropriate.
5. **Sources & Citations** — List all sources with clickable links.
6. **Risk Factors & Caveats** — Potential risks, limitations, and disclaimers.

## Tone & Style
- Use professional, objective financial language.
- Prefer quantitative statements (e.g., "revenue grew 12% YoY") over vague language.
- Use standard financial abbreviations: YoY, QoQ, CAGR, EBITDA, P/E, etc.
- Maintain a neutral, analytical tone — avoid promotional or speculative language.
- Format the entire report in clean Markdown with headers and sub-headers.
- Include a disclaimer at the end: "This report is for informational purposes only
  and does not constitute investment advice."

Always cite your sources. If data comes from an uploaded PDF, reference it by name.
If data comes from web search, include the URL.
"""


def writer_node(state: dict) -> dict:
    """
    LangGraph node: produce the final financial research report.

    Reads: query, plan, pdf_content, search_results
    Writes: report, status, messages
    """
    query = state.get("query", "")
    plan = state.get("plan", {})
    pdf_content = state.get("pdf_content", "")
    search_results = state.get("search_results", [])

    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        temperature=config.LLM_TEMPERATURE,
        api_key=config.OPENAI_API_KEY,
        max_tokens=config.WRITER_MAX_TOKENS,
    )

    # Build the context for the writer
    context_parts: list[str] = []

    context_parts.append(f"## Research Query\n{query}")

    if plan.get("writer_instructions"):
        context_parts.append(
            f"## Special Instructions\n{plan['writer_instructions']}"
        )

    if pdf_content:
        # Truncate if too long (keep first 12k chars to leave room for search)
        truncated = pdf_content[:12000]
        if len(pdf_content) > 12000:
            truncated += "\n\n[... PDF content truncated for length ...]"
        context_parts.append(f"## Extracted PDF Content\n{truncated}")

    if search_results:
        search_text_parts: list[str] = []
        for i, r in enumerate(search_results[:10], 1):
            search_text_parts.append(
                f"{i}. **{r.get('title', 'Untitled')}**\n"
                f"   URL: {r.get('url', 'N/A')}\n"
                f"   {r.get('content', '')}\n"
            )
        context_parts.append(
            "## Web Search Results\n" + "\n".join(search_text_parts)
        )

    if not pdf_content and not search_results:
        context_parts.append(
            "## Note\nNo PDF content or web search results were available. "
            "Please provide your best analysis based on your training knowledge, "
            "and clearly indicate when information is from your general knowledge."
        )

    user_content = "\n\n---\n\n".join(context_parts)

    messages = [
        SystemMessage(content=WRITER_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    report = response.content

    logger.info("Report generated (%d chars)", len(report))

    return {
        "report": report,
        "status": {
            **state.get("status", {}),
            "writer": "✅ Report generated",
        },
    }
