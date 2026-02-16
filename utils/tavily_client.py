"""
Tavily Web Search Client

Thin wrapper around the Tavily Python SDK.
Follows the Web Search SKILL.md specification.
"""

import logging
import time
from typing import Optional

from tavily import TavilyClient

import config

logger = logging.getLogger(__name__)


class TavilySearch:
    """Search the web using the Tavily API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.TAVILY_API_KEY
        if not self.api_key:
            logger.warning("TAVILY_API_KEY is not set — web search will be unavailable")
        self._client: Optional[TavilyClient] = None

    @property
    def client(self) -> TavilyClient:
        if self._client is None:
            if not self.api_key:
                raise ValueError("TAVILY_API_KEY is not configured")
            self._client = TavilyClient(api_key=self.api_key)
        return self._client

    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        search_depth: Optional[str] = None,
    ) -> list[dict]:
        """
        Perform a web search.

        Args:
            query: The search query.
            max_results: Number of results (default from config).
            search_depth: "basic" or "advanced" (default from config).

        Returns:
            List of dicts with keys: title, url, content, score.
        """
        max_results = max_results or config.TAVILY_MAX_RESULTS
        search_depth = search_depth or config.TAVILY_SEARCH_DEPTH

        for attempt in range(3):
            try:
                response = self.client.search(
                    query=query,
                    max_results=max_results,
                    search_depth=search_depth,
                )
                results = response.get("results", [])
                return [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", ""),
                        "score": r.get("score", 0.0),
                    }
                    for r in results
                ]
            except Exception as e:
                logger.warning("Tavily search attempt %d failed: %s", attempt + 1, e)
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    logger.error("All Tavily search attempts failed")
                    return []
