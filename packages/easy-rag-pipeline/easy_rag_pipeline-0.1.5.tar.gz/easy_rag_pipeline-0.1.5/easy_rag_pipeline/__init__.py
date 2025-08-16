"""
easy_rag_pipeline

A reusable and configurable RAG (Retrieval-Augmented Generation) pipeline.
"""

__version__ = "0.1.0"

from .config import load_config
from .pipeline import create_and_persist_vector_store, query_rag_pipeline, simple_rag_pipeline
from .utils import setup_logging
from .agents.elysia_agent import create_elysia_tree


# This makes it easy for users to import the main functions directly from the package
# e.g., from easy_rag_pipeline import simple_rag_pipeline
__all__ = [
    "load_config",
    "create_and_persist_vector_store",
    "query_rag_pipeline",
    "simple_rag_pipeline",
    "setup_logging",
    "create_elysia_tree",
]
