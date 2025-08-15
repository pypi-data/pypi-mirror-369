from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, TextLoader
import os
from typing import List, Optional
import re

# try to import tiktoken for token-based splitting; fall back gracefully
try:
    import tiktoken
except Exception:
    tiktoken = None

def load_pdf(file_path: str):
    """Loads a PDF file and returns a list of documents."""
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    # add source/title metadata when available
    for d in docs:
        d.metadata.setdefault('source', file_path)
        if 'title' not in d.metadata:
            d.metadata['title'] = os.path.splitext(os.path.basename(file_path))[0]
    return docs

def load_website(url: str):
    """Loads content from a website and returns a list of documents."""
    loader = WebBaseLoader(url)
    docs = loader.load()
    for d in docs:
        d.metadata.setdefault('source', url)
        d.metadata.setdefault('title', url)
    return docs

def load_text(file_path: str):
    """Loads a text file and returns a list of documents."""
    loader = TextLoader(file_path)
    docs = loader.load()
    for d in docs:
        d.metadata.setdefault('source', file_path)
        # use filename (without extension) as a best-effort title
        d.metadata.setdefault('title', os.path.splitext(os.path.basename(file_path))[0])
    return docs

def chunk_documents(
    docs: List,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    use_tokenizer: bool = False,
    model_name: str = "gpt-3.5-turbo",
    separators: Optional[List[str]] = None,
):
    """
    Chunk a list of documents into smaller pieces.

    By default this behaves exactly like the previous implementation (character-based
    splitting). To enable token-aware splitting (recommended for better semantic
    chunk boundaries with respect to model context limits), set `use_tokenizer=True`
    and provide a `model_name` supported by tiktoken.

    Args:
        docs (list): A list of langchain `Document` objects.
        chunk_size (int): Max size of each chunk (interpreted as characters unless
            `use_tokenizer=True`, in which case it's tokens).
        chunk_overlap (int): Overlap between chunks (characters or tokens).
        use_tokenizer (bool): Whether to count tokens (requires `tiktoken`).
        model_name (str): Model name used to select tiktoken encoding.
        separators (List[str], optional): Preferred separators for RecursiveCharacterTextSplitter.

    Returns:
        list: A list of chunked `Document` objects with added `chunk_id` metadata.
    """
    if not docs:
        return []

    # sensible default separators to keep sentences/paragraphs intact
    if separators is None:
        separators = ["\n\n", "\n", " ", ""]

    length_function = None
    if use_tokenizer and tiktoken is not None:
        try:
            enc = tiktoken.encoding_for_model(model_name)

            def length_function(text: str) -> int:
                return len(enc.encode(text))
        except Exception:
            # if tiktoken doesn't support the model, fallback to basic len
            length_function = None

    splitter_kwargs = dict(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
    )
    if length_function is not None:
        splitter_kwargs['length_function'] = length_function

    splitter = RecursiveCharacterTextSplitter(**splitter_kwargs)

    # Ensure important sections like an "Abstract" are preserved and discoverable.
    # If a document contains an explicit Abstract heading, extract it and prepend
    # it to the document content so embeddings and retrieval will surface it.
    abstract_re = re.compile(r"(?ims)^\s*abstract[:\-\s]*\n?(.*?)(?=\n\s*\n|\Z)")
    for d in docs:
        try:
            text = d.page_content or ""
            m = abstract_re.search(text)
            if m:
                abstract_text = m.group(1).strip()
                # don't overwrite existing metadata abstract if present
                meta = dict(d.metadata or {})
                if not meta.get('abstract'):
                    meta['abstract'] = abstract_text
                meta['has_abstract'] = True
                # Prepend the abstract to the front so chunker keeps it together
                d.page_content = f"Abstract: {abstract_text}\n\n{text}"
                d.metadata = meta
        except Exception:
            # best-effort; don't fail ingestion for malformed documents
            pass

    # Prepend title (if available) to the start of each document so the title
    # influences embeddings and retrieval. Do not duplicate if already present.
    for d in docs:
        try:
            title = (d.metadata or {}).get('title') or (d.metadata or {}).get('original_title')
            if title:
                text = d.page_content or ""
                if not text.lstrip().lower().startswith('title:'):
                    d.page_content = f"Title: {title}\n\n{text}"
        except Exception:
            pass

    chunks = splitter.split_documents(docs)

    # add helpful metadata to each chunk for downstream retrieval/context
    for idx, c in enumerate(chunks):
        # preserve existing metadata and add chunk-specific fields
        c.metadata = dict(c.metadata or {})
        c.metadata.setdefault('source', c.metadata.get('source'))
        # original document title if present
        c.metadata.setdefault('original_title', c.metadata.get('title'))
        c.metadata['chunk_id'] = idx
        # optional human-friendly short id
        c.metadata.setdefault('chunk_index', idx)

    return chunks
