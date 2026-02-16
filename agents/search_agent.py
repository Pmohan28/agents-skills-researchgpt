"""
Web Search Agent

Uses the Tavily API to search for current market data and information.
Follows the Web Search SKILL.md specification.
"""

import logging

from utils.tavily_client import TavilySearch

logger = logging.getLogger(__name__)


def search_agent_node(state: dict) -> dict:
    """
    LangGraph node: perform web searches based on the plan.

    Reads: plan
    Writes: search_results, status
    """
    plan = state.get("plan", {})
    search_queries = plan.get("search_queries", [])

    if not search_queries:
        # Fallback to the original query
        query = state.get("query", "")
        search_queries = [query] if query else []

    if not search_queries:
        return {
            "search_results": [],
            "status": {
                **state.get("status", {}),
                "search_agent": "⚠️ No search queries",
            },
        }

    searcher = TavilySearch()
    all_results: list[dict] = []

    for query in search_queries:
        try:
            results = searcher.search(query)
            for r in results:
                r["query"] = query  # Tag which query produced this result
            all_results.extend(results)
            logger.info("Search '%s' returned %d results", query, len(results))
        except Exception as e:
            logger.error("Search failed for '%s': %s", query, e)

    # Deduplicate by URL
    seen_urls: set[str] = set()
    unique_results: list[dict] = []
    for r in all_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)

    return {
        "search_results": unique_results,
        "status": {
            **state.get("status", {}),
            "search_agent": f"✅ Found {len(unique_results)} results",
        },
    }
