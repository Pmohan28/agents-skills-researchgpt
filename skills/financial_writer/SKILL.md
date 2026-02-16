---
name: Financial Writer
description: Synthesise research findings into professional financial-language reports
---

# Financial Writer Skill

## Purpose
Take raw research data (extracted PDF content and/or web search results) and
produce a polished, professional report written in **financial language**.
The report follows the conventions used in equity research notes, market
commentary, and investment memos.

## Inputs
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | `str` | Yes | The original research question |
| `pdf_content` | `str` | No | Extracted text from PDF documents |
| `search_results` | `list[dict]` | No | Web search results |

## Outputs
A Markdown-formatted report containing:
- **Executive Summary** — 2–3 sentence overview
- **Key Findings** — Bullet points with supporting data
- **Market Analysis** — Narrative discussion with financial terminology
- **Data & Metrics** — Tables of relevant numbers if available
- **Sources & Citations** — Links to sources used
- **Risk Factors** — Potential caveats and limitations

## Tone & Style Guidelines
- Use professional, objective financial language
- Prefer quantitative statements ("revenue grew 12% YoY") over vague language
- Use standard financial abbreviations: YoY, QoQ, CAGR, EBITDA, P/E, etc.
- Maintain a neutral, analytical tone — avoid promotional or speculative language
- Structure the report with clear headers and sub-headers
- Include disclaimers where appropriate

## Usage Example
```python
from agents.writer_agent import writer_node

state = {
    "query": "EV market outlook",
    "pdf_content": "...",
    "search_results": [...],
}
result = writer_node(state)
print(result["report"])
```

## Notes
- Uses an LLM with a financial-language system prompt.
- The system prompt enforces tone, structure, and terminology.
- Max output tokens controlled by `config.WRITER_MAX_TOKENS`.
