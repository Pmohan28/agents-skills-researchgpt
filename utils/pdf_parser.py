"""
PDF Parser Utility

Extracts text and tables from PDF files using pdfplumber.
Follows the PDF Extraction SKILL.md specification.
"""

import io
import logging
from typing import Optional, Union

import pdfplumber

import config

logger = logging.getLogger(__name__)


class PDFParser:
    """Extract structured content from PDF documents using pdfplumber."""

    # ── Public API ────────────────────────────────────────────────────────

    def extract(
        self,
        pdf_bytes: Optional[bytes] = None,
        file_path: Optional[str] = None,
    ) -> dict:
        """
        Extract text and tables from a PDF.

        Args:
            pdf_bytes: Raw PDF bytes (mutually exclusive with file_path).
            file_path: Path to a PDF on disk.

        Returns:
            dict with keys: text, tables, metadata
        """
        if pdf_bytes is not None:
            return self._extract_from_bytes(pdf_bytes)
        elif file_path is not None:
            return self._extract_from_path(file_path)
        else:
            raise ValueError("Provide either pdf_bytes or file_path")

    # ── Internal helpers ──────────────────────────────────────────────────

    def _extract_from_bytes(self, pdf_bytes: bytes) -> dict:
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            with pdfplumber.open(pdf_file) as pdf:
                return self._process_pdf(pdf)
        except Exception as e:
            logger.error("Error parsing PDF from bytes: %s", e)
            raise Exception(f"Error parsing PDF: {str(e)}")

    def _extract_from_path(self, file_path: str) -> dict:
        try:
            with pdfplumber.open(file_path) as pdf:
                return self._process_pdf(pdf)
        except Exception as e:
            logger.error("Error parsing PDF from file %s: %s", file_path, e)
            raise Exception(f"Error parsing PDF: {str(e)}")

    def _process_pdf(self, pdf) -> dict:
        max_pages = config.PDF_MAX_PAGES
        extract_tables = config.PDF_TABLE_EXTRACTION

        text_parts: list[str] = []
        tables: list[str] = []
        page_count = len(pdf.pages)

        for i, page in enumerate(pdf.pages[:max_pages]):
            # ── Text extraction ───────────────────────────────────────
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text_parts.append(f"--- Page {i + 1} ---\n{page_text.strip()}")

            # ── Table extraction ──────────────────────────────────────
            if extract_tables:
                try:
                    page_tables = page.extract_tables()
                    for t_idx, table in enumerate(page_tables):
                        md_table = self._table_to_markdown(table)
                        if md_table:
                            tables.append(
                                f"**Table (Page {i + 1}, #{t_idx + 1})**\n{md_table}"
                            )
                except Exception as e:
                    logger.warning(
                        "Could not extract table on page %d: %s", i + 1, e
                    )

        if not text_parts:
            raise ValueError("No text could be extracted from the PDF")

        metadata = {
            "page_count": page_count,
            "pages_processed": min(page_count, max_pages),
        }

        return {
            "text": "\n\n".join(text_parts),
            "tables": tables,
            "metadata": metadata,
        }

    @staticmethod
    def _table_to_markdown(table: list[list]) -> Optional[str]:
        """Convert a pdfplumber table (list-of-lists) to a Markdown table."""
        if not table or len(table) < 2:
            return None

        # Clean cells
        def clean(cell):
            return str(cell).strip().replace("\n", " ") if cell else ""

        header = [clean(c) for c in table[0]]
        rows = [[clean(c) for c in row] for row in table[1:]]

        md_lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(["---"] * len(header)) + " |",
        ]
        for row in rows:
            # Pad row to header length
            padded = row + [""] * (len(header) - len(row))
            md_lines.append("| " + " | ".join(padded[: len(header)]) + " |")

        return "\n".join(md_lines)
