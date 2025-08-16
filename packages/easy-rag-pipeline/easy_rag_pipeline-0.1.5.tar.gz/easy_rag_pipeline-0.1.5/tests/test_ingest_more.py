import os
from types import SimpleNamespace

import pytest

from easy_rag_pipeline.ingest import chunk_documents, load_text


class SimpleDoc:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}


def test_chunk_documents_title_and_abstract_prepended():
    doc = SimpleDoc(
        page_content="Abstract:\nThis is a short abstract.\n\nHere is the body text.",
        metadata={"title": "MyDoc"},
    )

    chunks = chunk_documents([doc], chunk_size=1000, chunk_overlap=0)
    assert len(chunks) == 1
    c = chunks[0]
    # chunk ids should be stable and human-friendly
    assert c.metadata["chunk_id"] == "0-0"
    assert c.metadata["chunk_global_index"] == 0
    assert c.metadata["chunk_index"] == 0
    # Title and Abstract should be present at the start of the content
    assert "Title: MyDoc" in c.page_content
    assert "Abstract: This is a short abstract." in c.page_content


def test_load_text_with_raganything_monkeypatch(monkeypatch, tmp_path):
    # Prepare a fake raganything parser and monkeypatch into ingest module
    fake_doc = SimpleNamespace(page_content="node text", metadata={})

    # Monkeypatch the ingest module's parse_with_raganything function
    import easy_rag_pipeline.ingest as ingest_mod

    monkeypatch.setattr(ingest_mod, "parse_with_raganything", lambda path, config=None: [fake_doc])

    # Create a dummy file path
    fp = tmp_path / "sample.txt"
    fp.write_text("hello world")

    docs = load_text(str(fp), parser="raganything")
    assert len(docs) == 1
    d = docs[0]
    # metadata should have source set to the path
    assert d.metadata["source"] == str(fp)
    # title should default to filename without extension
    assert d.metadata["title"] == fp.stem
