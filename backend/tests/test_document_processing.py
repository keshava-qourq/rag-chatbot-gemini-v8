"""Unit tests for app.document_processing.chunk_pdf_bytes.

This module is deliberately pure (its own docstring: "No database access and
no I/O here"), yet nothing in backend/tests exercises it directly -- the only
coverage it gets is incidental, through the worker's real-subprocess tests in
backend/tests/integration/test_worker_processing.py, which only proves a
single-page, short-text PDF chunks into exactly one chunk. These tests drive
the pure function itself with raw bytes: a corrupted file, a scanned/
image-only file, a genuinely multi-page PDF (page-anchored chunking, AC-017),
and a single page long enough to require more than one chunk (the CHUNK_SIZE
boundary the module's own constant defines).
"""

from __future__ import annotations

import io

import pytest
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from app.document_processing import (
    CHUNK_SIZE,
    CorruptedPDFError,
    NoExtractableTextError,
    chunk_pdf_bytes,
)


def _pdf_with_pages(texts: list[str]) -> bytes:
    """A minimal, genuinely valid multi-page PDF, one page per entry in
    ``texts``, each page's visible text being that entry."""
    writer = PdfWriter()
    font_ref = None
    for text in texts:
        page = writer.add_blank_page(width=200, height=200)

        stream_obj = DecodedStreamObject()
        stream_obj.set_data(f"BT /F1 24 Tf 10 100 Td ({text}) Tj ET".encode())
        stream_ref = writer._add_object(stream_obj)

        if font_ref is None:
            font = DictionaryObject()
            font[NameObject("/Type")] = NameObject("/Font")
            font[NameObject("/Subtype")] = NameObject("/Type1")
            font[NameObject("/BaseFont")] = NameObject("/Helvetica")
            font_ref = writer._add_object(font)

        resources = DictionaryObject()
        font_dict = DictionaryObject()
        font_dict[NameObject("/F1")] = font_ref
        resources[NameObject("/Font")] = font_dict
        page[NameObject("/Resources")] = resources
        page[NameObject("/Contents")] = stream_ref

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def _blank_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_ac017_multi_page_pdf_produces_chunks_each_anchored_to_their_own_page() -> None:
    pdf_bytes = _pdf_with_pages(["Alpha content page one", "Beta content page two"])

    result = chunk_pdf_bytes(pdf_bytes)

    assert result.page_count == 2
    assert len(result.chunks) >= 2
    pages_seen = {c.page_number for c in result.chunks}
    assert pages_seen == {1, 2}

    page_one_chunks = [c for c in result.chunks if c.page_number == 1]
    page_two_chunks = [c for c in result.chunks if c.page_number == 2]
    assert any("Alpha" in c.content for c in page_one_chunks)
    assert any("Beta" in c.content for c in page_two_chunks)
    # Each chunk is anchored to exactly its own page's text, not a mix.
    assert not any("Beta" in c.content for c in page_one_chunks)
    assert not any("Alpha" in c.content for c in page_two_chunks)

    # Chunk indices are sequential and ordered.
    assert [c.chunk_index for c in result.chunks] == list(range(len(result.chunks)))


def test_ac017_single_short_page_yields_exactly_one_chunk() -> None:
    result = chunk_pdf_bytes(_pdf_with_pages(["Just one short page of content"]))

    assert result.page_count == 1
    assert len(result.chunks) == 1
    assert result.chunks[0].page_number == 1
    assert result.chunks[0].chunk_index == 0
    assert result.chunks[0].content.strip() != ""


def test_long_page_text_splits_into_multiple_size_bounded_chunks() -> None:
    """A single page whose extracted text exceeds CHUNK_SIZE must split into
    more than one chunk, each no longer than CHUNK_SIZE, all on that same
    page, and reconstructing the original extracted text when concatenated."""
    pdf_bytes = _pdf_with_pages(["Lorem " * 500])

    result = chunk_pdf_bytes(pdf_bytes)

    from pypdf import PdfReader

    expected_text = (PdfReader(io.BytesIO(pdf_bytes)).pages[0].extract_text() or "").strip()

    assert result.page_count == 1
    assert len(expected_text) > CHUNK_SIZE, "fixture must actually exceed CHUNK_SIZE"
    assert len(result.chunks) > 1
    assert all(c.page_number == 1 for c in result.chunks)
    assert all(len(c.content) <= CHUNK_SIZE for c in result.chunks)
    assert [c.chunk_index for c in result.chunks] == list(range(len(result.chunks)))
    assert "".join(c.content for c in result.chunks) == expected_text


def test_ac020_corrupted_pdf_bytes_raise_corrupted_pdf_error() -> None:
    """Starts with a PDF header (so a content-sniffing check would pass it)
    but has no valid internal structure -- pypdf itself must fail on it."""
    garbage = b"%PDF-1.4\n" + b"this is not a real pdf structure, just garbage. " * 10

    with pytest.raises(CorruptedPDFError):
        chunk_pdf_bytes(garbage)


def test_ac020_entirely_non_pdf_bytes_raise_corrupted_pdf_error() -> None:
    with pytest.raises(CorruptedPDFError):
        chunk_pdf_bytes(b"not a pdf at all, just plain bytes")


def test_ac020_blank_page_pdf_with_no_extractable_text_raises_no_extractable_text_error() -> None:
    """A structurally valid PDF with zero extractable text on any page --
    standing in for a scanned/image-only PDF, which this pipeline does not
    OCR -- must be classified distinctly from a corrupted file."""
    with pytest.raises(NoExtractableTextError):
        chunk_pdf_bytes(_blank_pdf_bytes())


def test_ac020_multi_page_pdf_with_no_text_on_any_page_raises_no_extractable_text_error() -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)

    with pytest.raises(NoExtractableTextError):
        chunk_pdf_bytes(buf.getvalue())
