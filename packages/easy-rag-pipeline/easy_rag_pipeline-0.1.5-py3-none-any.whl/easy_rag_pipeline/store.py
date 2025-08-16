from langchain_community.vectorstores import FAISS
# To be added in the future:
# from langchain_community.vectorstores import Chroma, Pinecone, Weaviate
from typing import List

def create_vector_store(chunks: list, embedding_function, store_config: dict):
    """
    Creates a vector store from document chunks and an embedding function.

    Args:
        chunks (list): A list of document chunks.
        embedding_function: The embedding function to use.
        store_config (dict): Configuration for the vector store.
            Example:
            {
                "provider": "faiss"
            }

    Returns:
        A LangChain vector store object.
    """
    provider = store_config.get("provider", "faiss").lower()

    if provider == "faiss":
        # FAISS.from_documents creates the vector store in memory.
        # For persistence, you would use db.save_local(...) and FAISS.load_local(...)
        vector_db = FAISS.from_documents(documents=chunks, embedding=embedding_function)

        # Build a lightweight node_id -> docs map and adjacency graph from chunk metadata.
        # This enables simple vector-graph fusion retrieval without introducing a
        # heavyweight graph DB. We attach them to the vectorstore object so callers
        # can optionally use graph-based expansion during retrieval.
        nodeid_map = {}
        adjacency = {}

        for c in chunks:
            meta = dict(c.metadata or {})
            # Prefer explicit node_id if provided by upstream parser (e.g., raganything)
            node_id = meta.get('node_id') or meta.get('node') or str(meta.get('chunk_id', meta.get('chunk_index', None)))
            if node_id is None:
                continue
            nodeid_map.setdefault(node_id, []).append(c)

            # handle simple parent/belongs_to relations if present
            parent = meta.get('belongs_to') or meta.get('parent_id')
            if parent:
                adjacency.setdefault(node_id, set()).add(parent)
                adjacency.setdefault(parent, set()).add(node_id)

        # convert adjacency sets to lists for easier JSON-like use
        vector_db.nodeid_map = nodeid_map
        vector_db.graph = {k: list(v) for k, v in adjacency.items()}

        return vector_db
    # Example for Chroma (requires `pip install chromadb`)
    # elif provider == "chroma":
    #     return Chroma.from_documents(documents=chunks, embedding=embedding_function)
    else:
        raise ValueError(f"Unsupported vector store provider: {provider}")
