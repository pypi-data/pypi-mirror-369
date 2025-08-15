def retrieve_documents(
    query: str,
    vectorstore,
    k: int = 5,
    use_mmr: bool = False,
    fetch_k: int = 20,
    score_threshold: float = 0.0,
):
    """
    Retrieve documents from a vectorstore with a few retrieval strategies.

    By default this performs a standard similarity search. For better diversity and
    to reduce near-duplicate chunks, set `use_mmr=True` which will use maximal
    marginal relevance (MMR). `fetch_k` controls how many candidates to consider
    when doing MMR.

    Args:
        query (str): The user's query.
        vectorstore: LangChain-compatible vector store (must implement similarity_search or similar).
        k (int): Number of final documents to return.
        use_mmr (bool): If True, use `similarity_search_with_relevance_scores` + simple MMR.
        fetch_k (int): How many candidates to fetch before MMR re-ranking.
        score_threshold (float): Minimum similarity score to keep a document (if store returns scores).

    Returns:
        list: A list of retrieved documents.
    """
    # Try to use a vectorstore method that returns scores when needed
    if use_mmr and hasattr(vectorstore, 'similarity_search_with_relevance_scores'):
        results = vectorstore.similarity_search_with_relevance_scores(query, k=fetch_k)
        # results is a list of (doc, score)
        # apply score threshold if provided
        if score_threshold > 0.0:
            results = [(d, s) for (d, s) in results if s >= score_threshold]

        # simple greedy MMR implementation
        selected = []
        selected_texts = []

        # early exit
        if not results:
            return []

        # sort candidates by score descending
        candidates = sorted(results, key=lambda x: x[1], reverse=True)

        for doc, score in candidates:
            if len(selected) >= k:
                break
            # if no selected yet, pick the highest scored
            if not selected:
                selected.append(doc)
                selected_texts.append(doc.page_content)
                # keep the original score as metadata for downstream use (safe assignment)
                meta = dict(doc.metadata or {})
                try:
                    meta['score'] = float(score)
                except Exception:
                    # if score can't be cast, skip attaching it
                    pass
                doc.metadata = meta
                continue

            # compute a simple textual overlap penalty (naive MMR proxy)
            overlap = any(doc.page_content in t or t in doc.page_content for t in selected_texts)
            if not overlap:
                selected.append(doc)
                selected_texts.append(doc.page_content)

        return selected[:k]

    # fallback to standard similarity search
    if hasattr(vectorstore, 'similarity_search'):
        return vectorstore.similarity_search(query, k=k)

    # last resort: try a generic search call
    try:
        return vectorstore.search(query)[:k]
    except Exception as exc:
        raise ValueError('Vectorstore does not support known similarity search APIs') from exc
