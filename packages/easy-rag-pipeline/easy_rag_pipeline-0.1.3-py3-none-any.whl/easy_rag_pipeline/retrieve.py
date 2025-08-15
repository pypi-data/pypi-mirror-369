def retrieve_documents(query: str, vectorstore, k: int = 5):
    """
    Retrieves the most relevant documents from the vector store for a given query.

    Args:
        query (str): The user's query.
        vectorstore: The LangChain vector store object.
        k (int): The number of top documents to retrieve.

    Returns:
        list: A list of retrieved documents.
    """
    return vectorstore.similarity_search(query, k=k)
