"""
Module 1 — Document Ingestion & Parsing
=========================================
Turns an uploaded PDF/DOCX/PPTX into clean text plus a best-effort
title/abstract split, per Section 5 of the plan.
"""

import logging
import re
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document
from pptx import Presentation

log = logging.getLogger(__name__)


def parse_pdf(path: str) -> str:
    doc = fitz.open(path)
    try:
        return "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()


def parse_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def parse_pptx(path: str) -> str:
    prs = Presentation(path)
    out = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                out.append(shape.text_frame.text)
    return "\n".join(out)


PARSERS = {"pdf": parse_pdf, "docx": parse_docx, "pptx": parse_pptx}


def extract_text(storage_path: str, file_type: str) -> str:
    parser = PARSERS.get(file_type.lower())
    if not parser:
        log.warning("No parser for file_type=%s (%s); skipping.", file_type, storage_path)
        return ""
    try:
        return parser(storage_path)
    except Exception as e:
        log.error("Failed to parse %s (%s): %s", storage_path, file_type, e)
        return ""


_ABSTRACT_HEADERS = re.compile(r"\babstract\b", re.IGNORECASE)
_SECTION_HEADERS = re.compile(
    r"\b(introduction|1\.\s|chapter\s*1|table of contents|keywords)\b", re.IGNORECASE
)


def split_title_abstract(full_text: str, fallback_title: str = "") -> dict:
    """
    Lightweight heuristic split (Section 5, step 4). Looks for an "Abstract"
    heading and grabs the text up to the next section header. First non-empty
    line becomes the title if none is supplied.
    """
    lines = [l.strip() for l in full_text.splitlines() if l.strip()]
    title = fallback_title or (lines[0] if lines else "Untitled Project")

    m = _ABSTRACT_HEADERS.search(full_text)
    abstract = ""
    if m:
        after = full_text[m.end():]
        end = _SECTION_HEADERS.search(after)
        abstract = after[: end.start()] if end else after[:2000]
        abstract = abstract.strip(" :\n\t")
    if not abstract:
        # Fallback: first ~120 words of body text
        abstract = " ".join(full_text.split()[:120])

    return {"title": title.strip(), "abstract": abstract.strip(), "full_text": full_text}
