"""Pure PDF parsing/chunking logic: PDF bytes in, page-anchored chunks out.

No database access and no I/O here -- app.jobs.process_document is the only
caller, and it owns fetching the bytes (via app.storage.load) and persisting
results. Keeping this pure makes it trivial to unit test with raw bytes.

Two distinct failure modes are classified so the caller can set a specific,
human-readable Document.error_message for each (AC-020):

- CorruptedPDFError: pypdf itself could not read the file.
- NoExtractableTextError: pypdf read it fine, but every page's extracted text
  is empty/whitespace -- almost always a scanned/image-only PDF, which this
  project does not OCR.
"""

from __future__ import annotations

import io
from dataclasses import dataclass

from pypdf import PdfReader
from pypdf.errors import PdfReadError

# Target chunk size in characters. A page's text is sliced into pieces of at
# most this size; a chunk never spans two pages, so short pages simply yield a
# single, smaller chunk.
CHUNK_SIZE = 1000


class CorruptedPDFError(Exception):
    """Raised when pypdf cannot read the file at all."""


class NoExtractableTextError(Exception):
    """Raised when every page's extracted text is empty or whitespace-only."""


@dataclass(frozen=True)
class Chunk:
    """One page-anchored slice of extracted text, ready to become a DocumentChunk."""

    chunk_index: int
    page_number: int
    content: str


@dataclass(frozen=True)
class ParsedDocument:
    """The result of parsing and chunking a PDF: its chunks plus its total
    page count (documents.page_count -- shown in the Documents list once a
    document reaches 'ready', see docs/sdlc/architecture/data-model.md)."""

    chunks: list[Chunk]
    page_count: int


def chunk_pdf_bytes(data: bytes) -> ParsedDocument:
    """Extract text per page from ``data``, split it into ordered chunks, and
    count its pages.

    Raises CorruptedPDFError if pypdf cannot read the file, or
    NoExtractableTextError if it reads fine but contains no extractable text
    on any page (e.g. a scanned/image-only PDF). Never returns an empty chunk
    list on success: if it returns, there is at least one chunk.
    """
    try:
        reader = PdfReader(io.BytesIO(data))
        pages_text = [page.extract_text() or "" for page in reader.pages]
    except (PdfReadError, ValueError, KeyError, OSError) as exc:
        raise CorruptedPDFError(str(exc)) from exc

    if not any(text.strip() for text in pages_text):
        raise NoExtractableTextError(
            "No extractable text found on any page; this PDF may be scanned or image-only."
        )

    chunks: list[Chunk] = []
    index = 0
    for page_number, text in enumerate(pages_text, start=1):
        stripped = text.strip()
        if not stripped:
            continue
        for start in range(0, len(stripped), CHUNK_SIZE):
            piece = stripped[start : start + CHUNK_SIZE]
            chunks.append(Chunk(chunk_index=index, page_number=page_number, content=piece))
            index += 1

    return ParsedDocument(chunks=chunks, page_count=len(pages_text))
