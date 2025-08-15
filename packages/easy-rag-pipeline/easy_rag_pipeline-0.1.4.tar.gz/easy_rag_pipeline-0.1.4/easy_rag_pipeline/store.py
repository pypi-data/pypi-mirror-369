from langchain_community.vectorstores import FAISS
# To be added in the future:
# from langchain_community.vectorstores import Chroma, Pinecone, Weaviate

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
        return vector_db
    # Example for Chroma (requires `pip install chromadb`)
    # elif provider == "chroma":
    #     return Chroma.from_documents(documents=chunks, embedding=embedding_function)
    else:
        raise ValueError(f"Unsupported vector store provider: {provider}")
