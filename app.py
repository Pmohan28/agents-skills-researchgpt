"""
Market Research GPT — Streamlit Application

A multi-agent market research assistant powered by LangGraph.
Upload PDFs, ask research questions, and get professional financial reports.
"""

import logging
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

import config
from agents.graph import research_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Market Research GPT",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 40%, #24243e 100%);
}

/* Main header */
.main-header {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 50%, #6366f1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    padding: 1rem 0 0.25rem;
    letter-spacing: -0.5px;
}
.sub-header {
    text-align: center;
    color: rgba(255,255,255,0.55);
    font-size: 1rem;
    font-weight: 400;
    margin-bottom: 1.5rem;
}

/* Glass cards */
.glass-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(99,102,241,0.15);
}

/* Agent status badges */
.agent-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0.35rem 0.85rem;
    border-radius: 24px;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 0.2rem 0.25rem;
}
.badge-planner {
    background: rgba(99,102,241,0.15);
    color: #a5b4fc;
    border: 1px solid rgba(99,102,241,0.3);
}
.badge-pdf {
    background: rgba(236,72,153,0.15);
    color: #f9a8d4;
    border: 1px solid rgba(236,72,153,0.3);
}
.badge-search {
    background: rgba(34,211,238,0.15);
    color: #67e8f9;
    border: 1px solid rgba(34,211,238,0.3);
}
.badge-writer {
    background: rgba(52,211,153,0.15);
    color: #6ee7b7;
    border: 1px solid rgba(52,211,153,0.3);
}

/* Chat messages */
.user-msg {
    background: linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(139,92,246,0.2) 100%);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 16px 16px 4px 16px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    color: #e2e8f0;
}
.ai-msg {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px 16px 16px 4px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    color: #cbd5e1;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a3e 0%, #0f0c29 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e2e8f0;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(99,102,241,0.4);
}

/* File uploader */
.stFileUploader > div {
    border-radius: 12px;
    border: 1px dashed rgba(99,102,241,0.4);
}

/* Spinner */
.stSpinner > div {
    border-color: #6366f1 !important;
}

/* Metrics */
.metric-row {
    display: flex;
    gap: 0.75rem;
    margin: 0.5rem 0;
}
.metric-card {
    flex: 1;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 0.75rem;
    text-align: center;
}
.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00d2ff, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-label {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.45);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(135deg, #059669 0%, #34d399 100%);
    color: white;
    border: none;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "messages": [],
        "uploaded_files_data": [],
        "agent_status": {},
        "research_count": 0,
        "current_report": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown('<p class="main-header" style="font-size:1.6rem;">📊 Market Research GPT</p>', unsafe_allow_html=True)
        st.markdown("---")

        # PDF Upload
        st.markdown("### 📄 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload PDF files for analysis",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload annual reports, earnings notes, or any financial PDFs",
        )

        if uploaded_files:
            st.session_state["uploaded_files_data"] = [
                {"name": f.name, "bytes": f.read()} for f in uploaded_files
            ]
            st.markdown(f"""
            <div class="glass-card">
                <strong style="color:#a5b4fc;">📎 {len(uploaded_files)} file(s) loaded</strong><br>
                <span style="color:rgba(255,255,255,0.5);font-size:0.85rem;">
                    {', '.join(f.name for f in uploaded_files)}
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.session_state["uploaded_files_data"] = []

        st.markdown("---")

        # Agent Status
        st.markdown("### 🤖 Agent Activity")
        status = st.session_state.get("agent_status", {})
        if status:
            badge_classes = {
                "planner": "badge-planner",
                "pdf_agent": "badge-pdf",
                "search_agent": "badge-search",
                "writer": "badge-writer",
            }
            badge_icons = {
                "planner": "🧠",
                "pdf_agent": "📄",
                "search_agent": "🔍",
                "writer": "✍️",
            }
            for agent, stat in status.items():
                cls = badge_classes.get(agent, "badge-planner")
                icon = badge_icons.get(agent, "🔧")
                st.markdown(
                    f'<span class="agent-badge {cls}">{icon} {agent}: {stat}</span>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<span style="color:rgba(255,255,255,0.35);font-size:0.85rem;">'
                "No agents active</span>",
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Stats
        st.markdown("### 📈 Session Stats")
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-value">{st.session_state.get("research_count", 0)}</div>
                <div class="metric-label">Queries</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(st.session_state.get("uploaded_files_data", []))}</div>
                <div class="metric-label">PDFs</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Clear chat
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["agent_status"] = {}
            st.session_state["current_report"] = ""
            st.rerun()

        # About
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Market Research GPT** uses a multi-agent pipeline:

            1. 🧠 **Planner** — Decomposes your query
            2. 📄 **PDF Agent** — Extracts document content
            3. 🔍 **Search Agent** — Finds current market data
            4. ✍️ **Writer** — Produces a financial report

            Built with **LangGraph** + **Streamlit**.
            """)


# ── Research Pipeline ─────────────────────────────────────────────────────────
def run_research(query: str):
    """Execute the full LangGraph research pipeline."""
    uploaded = st.session_state.get("uploaded_files_data", [])

    initial_state = {
        "query": query,
        "plan": {},
        "uploaded_files": uploaded,
        "pdf_content": "",
        "search_results": [],
        "report": "",
        "status": {},
        "messages": [HumanMessage(content=query)],
    }

    status_container = st.empty()

    # Stream through the graph to show progress
    final_state = None
    with st.spinner("🔬 Research agents are working..."):
        try:
            for step in research_graph.stream(initial_state):
                # Each step is {node_name: state_update}
                for node_name, state_update in step.items():
                    new_status = state_update.get("status", {})
                    if new_status:
                        st.session_state["agent_status"].update(new_status)

                    # Show live agent activity
                    badge_map = {
                        "planner": ("🧠", "badge-planner"),
                        "pdf_agent": ("📄", "badge-pdf"),
                        "search_agent": ("🔍", "badge-search"),
                        "writer": ("✍️", "badge-writer"),
                    }
                    icon, cls = badge_map.get(node_name, ("🔧", "badge-planner"))
                    status_container.markdown(
                        f'<div class="glass-card">'
                        f'<span class="agent-badge {cls}">{icon} {node_name}</span> '
                        f'<span style="color:rgba(255,255,255,0.6);">processing...</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    if "report" in state_update and state_update["report"]:
                        final_state = state_update

        except Exception as e:
            st.error(f"❌ Research pipeline error: {e}")
            logger.error("Pipeline error: %s", e, exc_info=True)
            return None

    status_container.empty()

    if final_state and final_state.get("report"):
        st.session_state["research_count"] += 1
        st.session_state["current_report"] = final_state["report"]
        return final_state["report"]

    return None


# ── Main Content ──────────────────────────────────────────────────────────────
def render_main():
    st.markdown('<h1 class="main-header">📊 Market Research GPT</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Multi-agent financial research powered by LangGraph</p>',
        unsafe_allow_html=True,
    )

    # ── Chat History ──────────────────────────────────────────────────────
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="user-msg"><strong>🧑 You</strong><br>{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="ai-msg"><strong>📊 Research Report</strong></div>',
                unsafe_allow_html=True,
            )
            st.markdown(msg["content"])

    # ── Input ─────────────────────────────────────────────────────────────
    query = st.chat_input(
        "Ask a market research question... (e.g. 'Analyse the EV market outlook for 2025')"
    )

    if query:
        # Add user message
        st.session_state["messages"].append({"role": "user", "content": query})
        st.markdown(
            f'<div class="user-msg"><strong>🧑 You</strong><br>{query}</div>',
            unsafe_allow_html=True,
        )

        # Run research
        report = run_research(query)

        if report:
            st.session_state["messages"].append({"role": "assistant", "content": report})
            st.markdown(
                '<div class="ai-msg"><strong>📊 Research Report</strong></div>',
                unsafe_allow_html=True,
            )
            st.markdown(report)

            # Download button
            col1, col2, _ = st.columns([1, 1, 3])
            with col1:
                st.download_button(
                    label="📥 Download Report",
                    data=report,
                    file_name="market_research_report.md",
                    mime="text/markdown",
                )
            with col2:
                st.download_button(
                    label="📋 Copy as Text",
                    data=report,
                    file_name="market_research_report.txt",
                    mime="text/plain",
                )
        else:
            st.warning("⚠️ Could not generate a report. Check your API keys and try again.")


# ── Entrypoint ────────────────────────────────────────────────────────────────
def main():
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()
