# 📊 Market Research GPT

A multi-agent market research assistant powered by **LangGraph** and **Streamlit**.
Upload PDFs, ask financial research questions, and receive professional reports
written in financial language.

## Architecture

```
User Query → Planner Agent → [PDF Agent | Search Agent] → Financial Writer Agent → Report
```

| Agent | Purpose | Library |
|-------|---------|---------|
| 🧠 Planner | Decomposes queries into sub-tasks | LangGraph + OpenAI |
| 📄 PDF Agent | Extracts text & tables from PDFs | pdfplumber |
| 🔍 Search Agent | Searches the web for market data | Tavily |
| ✍️ Writer Agent | Writes professional financial reports | OpenAI |

## Quick Start

### 1. Install `uv` (if needed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create venv & install dependencies

```bash
uv venv
uv pip install -e .
```

### 3. Set API keys

```bash
cp .env.example .env
# Edit .env with your keys
```

Required keys:
- `OPENAI_API_KEY` — OpenAI API key
- `TAVILY_API_KEY` — Tavily search API key
- `LANGSMITH_API_KEY` — *(optional)* LangSmith tracing

### 4. Run the app

```bash
uv run streamlit run app.py
```

## Skills

Each sub-agent follows a documented skill in `skills/`:

- [`skills/pdf_extraction/SKILL.md`](skills/pdf_extraction/SKILL.md) — PDF parsing
- [`skills/web_search/SKILL.md`](skills/web_search/SKILL.md) — Web search
- [`skills/financial_writer/SKILL.md`](skills/financial_writer/SKILL.md) — Report writing

## Project Structure

```
agents-skill-mcp/
├── app.py                          # Streamlit UI
├── config.py                       # Configuration & env vars
├── pyproject.toml                  # uv / pip package definition
├── agents/
│   ├── state.py                    # LangGraph shared state
│   ├── orchestrator.py             # Planner node
│   ├── pdf_agent.py                # PDF extraction node
│   ├── search_agent.py             # Web search node
│   ├── writer_agent.py             # Financial writer node
│   └── graph.py                    # LangGraph StateGraph wiring
├── utils/
│   ├── pdf_parser.py               # pdfplumber wrapper
│   └── tavily_client.py            # Tavily API wrapper
└── skills/
    ├── pdf_extraction/SKILL.md
    ├── web_search/SKILL.md
    └── financial_writer/SKILL.md
```
