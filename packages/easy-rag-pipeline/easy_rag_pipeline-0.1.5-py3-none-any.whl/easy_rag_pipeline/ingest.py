from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, TextLoader
import os
from typing import List, Optional
import re
import logging
import warnings

# optional adapter import (lazy usage below)
try:
    from .adapters.raganything_adapter import parse_with_raganything
except Exception:
    parse_with_raganything = None

# try to import tiktoken for token-based splitting; fall back gracefully
try:
    import tiktoken
except Exception:
    tiktoken = None

# module-wide logger
logger = logging.getLogger(__name__)

def load_pdf(file_path: str, parser: str = 'builtin', parser_config: dict = None):
    """Loads a PDF file and returns a list of documents.

    parser: 'builtin' uses the repository's PyPDFLoader parsing, while
    'raganything' will call the optional RAG-Anything adapter (if installed).
    """
    parser_config = parser_config or {}
    # validate input
    if not isinstance(file_path, str) or not file_path:
        raise ValueError('file_path must be a non-empty string')
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'PDF file not found: {file_path}')
    if parser == 'raganything':
        if parse_with_raganything is None:
            raise ImportError('RAG-Anything adapter not available; install raganything or remove parser="raganything"')
        docs = parse_with_raganything(file_path, config=parser_config)
    else:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
    # add source/title metadata when available
    for d in docs:
        d.metadata.setdefault('source', file_path)
        if 'title' not in d.metadata:
            d.metadata['title'] = os.path.splitext(os.path.basename(file_path))[0]
    return docs

def load_website(url: str, parser: str = 'builtin', parser_config: dict = None):
    """Loads content from a website and returns a list of documents."""
    parser_config = parser_config or {}
    if not isinstance(url, str) or not url:
        raise ValueError('url must be a non-empty string')
    if not url.lower().startswith(('http://', 'https://')):
        raise ValueError('url must start with http:// or https://')
    if parser == 'raganything':
        if parse_with_raganything is None:
            raise ImportError('RAG-Anything adapter not available; install raganything or remove parser="raganything"')
        docs = parse_with_raganything(url, config=parser_config)
    else:
        loader = WebBaseLoader(url)
        docs = loader.load()
    for d in docs:
        d.metadata.setdefault('source', url)
        d.metadata.setdefault('title', url)
    return docs

def load_text(file_path: str, parser: str = 'builtin', parser_config: dict = None):
    """Loads a text file and returns a list of documents."""
    parser_config = parser_config or {}
    if not isinstance(file_path, str) or not file_path:
        raise ValueError('file_path must be a non-empty string')
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'Text file not found: {file_path}')
    if parser == 'raganything':
        if parse_with_raganything is None:
            raise ImportError('RAG-Anything adapter not available; install raganything or remove parser="raganything"')
        docs = parse_with_raganything(file_path, config=parser_config)
    else:
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
    if use_tokenizer:
        if tiktoken is None:
            warnings.warn('tiktoken not available; falling back to character-based splitting')
        else:
            try:
                enc = tiktoken.encoding_for_model(model_name)

                def length_function(text: str) -> int:
                    return len(enc.encode(text))
            except Exception:
                # if tiktoken doesn't support the model, fallback to basic len
                logger.debug('tiktoken encoding_for_model failed, falling back to len(text)')
                length_function = lambda s: len(s)

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

    # Split documents individually so we can attach stable per-document chunk ids
    chunks = []
    global_idx = 0
    for doc_idx, d in enumerate(docs):
        try:
            part_chunks = splitter.split_documents([d])
        except Exception:
            logger.exception('splitter failed on document; skipping document index %s', doc_idx)
            continue
        for local_idx, c in enumerate(part_chunks):
            c.metadata = dict(c.metadata or {})
            # preserve source/title if present; otherwise set to best-effort values
            c.metadata['source'] = c.metadata.get('source') or d.metadata.get('source') or 'unknown'
            c.metadata['original_title'] = c.metadata.get('original_title') or d.metadata.get('title') or d.metadata.get('original_title')
            # chunk identifiers: stable and human-friendly
            c.metadata['chunk_id'] = f"{doc_idx}-{local_idx}"
            c.metadata['chunk_global_index'] = global_idx
            c.metadata['chunk_index'] = local_idx
            chunks.append(c)
            global_idx += 1

    return chunks
