---
name: PDF Extraction
description: Extract text and tables from PDF documents using pdfplumber
---

# PDF Extraction Skill

## Purpose
Extract structured content from uploaded PDF documents — including plain text
and tabular data — so that downstream agents can reason over the document.

## Inputs
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pdf_bytes` | `bytes` | Yes (or `file_path`) | Raw PDF file bytes |
| `file_path` | `str` | Yes (or `pdf_bytes`) | Absolute path to a PDF file |

## Outputs
A dictionary with:
- `text` — Full extracted text, annotated with page numbers.
- `tables` — List of tables found, each rendered as a Markdown table.
- `metadata` — Page count, author, title (if available).

## Library
Uses **pdfplumber** (`import pdfplumber`).

## Usage Example
```python
from utils.pdf_parser import PDFParser

parser = PDFParser()
result = parser.extract(pdf_bytes=uploaded_file.read())
print(result["text"])
print(result["tables"])
```

## Error Handling
- Returns an error message if the PDF is encrypted or corrupt.
- Skips blank pages silently.
- Tables that cannot be parsed are logged and skipped.

## Notes
- Maximum supported page count is controlled by `config.PDF_MAX_PAGES`.
- Table extraction can be toggled via `config.PDF_TABLE_EXTRACTION`.
