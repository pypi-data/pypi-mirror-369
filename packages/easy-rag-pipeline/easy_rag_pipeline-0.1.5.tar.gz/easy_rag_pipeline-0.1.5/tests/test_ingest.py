import pytest
import os
import sys

# Add root project directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from easy_rag_pipeline.ingest import chunk_documents
from langchain_core.documents import Document

def test_chunk_documents():
    """
    Tests the chunk_documents function to ensure it splits documents correctly.
    """
    # Create a long document
    long_text = "This is a very long sentence. " * 20
    doc = Document(page_content=long_text)

    # Test chunking with a small chunk size
    chunks = chunk_documents([doc], chunk_size=50, chunk_overlap=10)

    # Assert that the document was split into multiple chunks
    assert len(chunks) > 1

    # Assert that each chunk is a Document object
    assert all(isinstance(chunk, Document) for chunk in chunks)

    # Assert that the content of the first chunk is smaller than the original
    assert len(chunks[0].page_content) < len(long_text)
    assert len(chunks[0].page_content) <= 50

def test_chunk_documents_with_no_split():
    """
    Tests that a short document is not split if it's smaller than the chunk size.
    """
    short_text = "This is a short sentence."
    doc = Document(page_content=short_text)

    chunks = chunk_documents([doc], chunk_size=100, chunk_overlap=10)

    # Assert that the document was not split
    assert len(chunks) == 1
    assert chunks[0].page_content == short_text
