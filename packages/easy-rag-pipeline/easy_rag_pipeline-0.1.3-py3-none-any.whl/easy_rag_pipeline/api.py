"""
High-level utility functions for easy RAG pipeline usage.
"""
from .pipeline import simple_rag_pipeline, create_and_persist_vector_store, query_rag_pipeline
from .config import load_config
import os


def rag_from_file(query: str, file_path: str, config_path: str) -> str:
    """
    Run RAG pipeline on a local text file.
    """
    config = load_config(config_path)
    return simple_rag_pipeline(query, file_path, 'txt', config)


def rag_from_url(query: str, url: str, config_path: str) -> str:
    """
    Run RAG pipeline on a website URL.
    """
    config = load_config(config_path)
    return simple_rag_pipeline(query, url, 'website', config)


def rag_from_text(query: str, text: str, config_path: str) -> str:
    """
    Run RAG pipeline on a string of text (saves to temp file).
    """
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as tmp:
        tmp.write(text)
        tmp_path = tmp.name
    config = load_config(config_path)
    result = simple_rag_pipeline(query, tmp_path, 'txt', config)
    os.remove(tmp_path)
    return result


def index_file(file_path: str, config_path: str, save_path: str = 'vector_store'):
    """
    Index a file and persist the vector store.
    """
    config = load_config(config_path)
    return create_and_persist_vector_store(file_path, 'txt', config, save_path)


def load_index_and_query(query: str, index_path: str, config_path: str) -> str:
    """
    Load a persisted vector store and query it.
    """
    from langchain_community.vectorstores.faiss import FAISS
    config = load_config(config_path)
    embedding_function = config['embedding']
    # Recreate embedding function
    from .embed import get_embedding_function
    embedding_fn = get_embedding_function(embedding_function)
    vector_store = FAISS.load_local(index_path, embedding_fn, allow_dangerous_deserialization=True)
    return query_rag_pipeline(query, vector_store, config)
