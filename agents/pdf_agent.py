"""
PDF Extraction Agent

Reads uploaded PDF files from state, extracts text and tables using
pdfplumber (via utils.pdf_parser), and writes results back to state.

Follows the PDF Extraction SKILL.md specification.
"""

import logging

from utils.pdf_parser import PDFParser

logger = logging.getLogger(__name__)


def pdf_agent_node(state: dict) -> dict:
    """
    LangGraph node: extract content from uploaded PDFs.

    Reads: uploaded_files, plan
    Writes: pdf_content, status
    """
    uploaded_files = state.get("uploaded_files", [])
    plan = state.get("plan", {})

    if not uploaded_files:
        return {
            "pdf_content": "",
            "status": {**state.get("status", {}), "pdf_agent": "⚠️ No PDFs to process"},
        }

    parser = PDFParser()
    all_text_parts: list[str] = []
    all_tables: list[str] = []

    for file_info in uploaded_files:
        name = file_info.get("name", "unknown.pdf")
        pdf_bytes = file_info.get("bytes", b"")

        try:
            result = parser.extract(pdf_bytes=pdf_bytes)
            all_text_parts.append(f"## 📄 {name}\n\n{result['text']}")

            if result.get("tables"):
                all_tables.extend(
                    [f"### Tables from {name}\n{t}" for t in result["tables"]]
                )

            meta = result.get("metadata", {})
            logger.info(
                "Extracted %d pages from %s",
                meta.get("pages_processed", 0),
                name,
            )
        except Exception as e:
            logger.error("Failed to extract from %s: %s", name, e)
            all_text_parts.append(f"## 📄 {name}\n\n⚠️ Error extracting: {e}")

    # Combine everything
    combined = "\n\n".join(all_text_parts)
    if all_tables:
        combined += "\n\n---\n# Extracted Tables\n\n" + "\n\n".join(all_tables)

    return {
        "pdf_content": combined,
        "status": {
            **state.get("status", {}),
            "pdf_agent": f"✅ Extracted {len(uploaded_files)} PDF(s)",
        },
    }
