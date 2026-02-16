---
name: Web Search
description: Search the internet for current market data using the Tavily API
---

# Web Search Skill

## Purpose
Perform real-time web searches to retrieve current market data, news, company
information, and industry trends relevant to the user's research query.

## Inputs
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | `str` | Yes | The search query string |
| `max_results` | `int` | No | Max number of results (default: 5) |
| `search_depth` | `str` | No | `"basic"` or `"advanced"` (default: `"advanced"`) |

## Outputs
A list of result dictionaries, each containing:
- `title` — Page title
- `url` — Source URL
- `content` — Snippet / summary of the page
- `score` — Relevance score (0–1)

## Library
Uses **tavily-python** SDK (`from tavily import TavilyClient`).

## Usage Example
```python
from utils.tavily_client import TavilySearch

searcher = TavilySearch()
results = searcher.search("electric vehicle market trends 2025")
for r in results:
    print(r["title"], r["url"])
```

## Error Handling
- Returns an empty list and logs a warning if the API key is missing.
- Retries transient errors up to 2 times with exponential backoff.

## Notes
- API key is read from `config.TAVILY_API_KEY`.
- `search_depth="advanced"` costs more credits but returns richer snippets.
