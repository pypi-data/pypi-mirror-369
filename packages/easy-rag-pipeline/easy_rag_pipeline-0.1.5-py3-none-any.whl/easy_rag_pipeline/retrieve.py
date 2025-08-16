import logging


logger = logging.getLogger(__name__)


def retrieve_documents(
    query: str,
    vectorstore,
    k: int = 5,
    use_mmr: bool = False,
    fetch_k: int = 20,
    score_threshold: float = 0.0,
    use_graph: bool = False,
    graph_alpha: float = 0.8,
    graph_beta: float = 0.2,
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
    # basic input validation
    if not isinstance(query, str) or not query.strip():
        logger.debug('Empty or invalid query provided to retrieve_documents')
        return []

    # Try to use a vectorstore method that returns scores when needed
    if use_mmr and hasattr(vectorstore, 'similarity_search_with_relevance_scores'):
        results = vectorstore.similarity_search_with_relevance_scores(query, k=fetch_k)
        # results is a list of (doc, score)
        # apply score threshold if provided
        if score_threshold > 0.0:
            try:
                results = [(d, s) for (d, s) in results if float(s) >= score_threshold]
            except Exception:
                # if scores aren't numeric, skip thresholding but log
                logger.debug('Could not apply score_threshold due to non-numeric scores')

    # simple greedy MMR implementation
        selected = []
        selected_texts = []

        # early exit
        if not results:
            return []

        # sort candidates by score descending (safely cast scores)
        def _score_key(item):
            try:
                return float(item[1])
            except Exception:
                return 0.0

        candidates = sorted(results, key=_score_key, reverse=True)

        for doc, score in candidates:
            if len(selected) >= k:
                break
            # if no selected yet, pick the highest scored
            if not selected:
                selected.append(doc)
                selected_texts.append(doc.page_content)
                # keep the original score as metadata for downstream use (safe assignment)
                meta = dict(getattr(doc, 'metadata', {}) or {})
                try:
                    meta['score'] = float(score)
                except Exception:
                    meta['score'] = None
                doc.metadata = meta
                continue

            # compute a simple textual overlap penalty (naive MMR proxy)
            try:
                overlap = any(doc.page_content in t or t in doc.page_content for t in selected_texts)
            except Exception:
                # defensive: if page_content is non-string, treat as non-overlapping
                overlap = False
            if not overlap:
                selected.append(doc)
                selected_texts.append(doc.page_content)

        return selected[:k]

    # If requested, perform vector-graph fusion: expand vector candidates by 1-hop
    # neighbors in the attached graph and re-rank by combined score.
    if use_graph:
        # require the vectorstore to have graph/nodeid_map attributes (attached in store.create_vector_store)
        if not hasattr(vectorstore, 'graph') or not hasattr(vectorstore, 'nodeid_map'):
            # fallback to plain similarity search if graph not available
            if hasattr(vectorstore, 'similarity_search'):
                return vectorstore.similarity_search(query, k=k)
            else:
                return []

        # fetch initial candidates with scores
        try:
            if hasattr(vectorstore, 'similarity_search_with_relevance_scores'):
                candidates = vectorstore.similarity_search_with_relevance_scores(query, k=fetch_k)
            else:
                # similarity_search may not return scores; simulate scores by ranking order
                docs = vectorstore.similarity_search(query, k=fetch_k)
                candidates = [(d, float(fetch_k - i)) for i, d in enumerate(docs)]
        except Exception:
            logger.exception('Failed to fetch initial candidates from vectorstore')
            return []

        # build a map from node_id to best vector score among its docs
        node_best_score = {}
        candidate_nodes = set()
        for doc, score in candidates:
            meta = dict(getattr(doc, 'metadata', {}) or {})
            node_id = meta.get('node_id') or meta.get('node') or meta.get('chunk_id') or meta.get('chunk_index')
            if node_id is None:
                # attempt to derive from source/text fallback
                node_id = str(meta.get('source') or '')
            node_id = str(node_id) if node_id is not None else ''
            if node_id:
                candidate_nodes.add(node_id)
                try:
                    sc = float(score)
                except Exception:
                    sc = 0.0
                node_best_score[node_id] = max(node_best_score.get(node_id, 0.0), sc)

        # expand by one-hop neighbors
        expanded_nodes = set(candidate_nodes)
        for n in list(candidate_nodes):
            neighbors = vectorstore.graph.get(n, [])
            for nb in neighbors:
                expanded_nodes.add(nb)

        # Collect all docs for expanded nodes and compute combined scores
        scored_docs = []
        for node in expanded_nodes:
            docs = vectorstore.nodeid_map.get(node, [])
            graph_score = 1.0 if node in candidate_nodes else 0.5
            # for each doc under this node, derive combined score
            for d in docs:
                vec_score = node_best_score.get(node, 0.0)
                combined = graph_alpha * vec_score + graph_beta * graph_score
                scored_docs.append((d, combined))

        # sort by combined score and deduplicate by text
        unique = {}
        for d, s in sorted(scored_docs, key=lambda x: x[1], reverse=True):
            try:
                key = (d.metadata.get('source'), d.page_content[:200]) if getattr(d, 'metadata', None) else d.page_content[:200]
            except Exception:
                key = getattr(d, 'page_content', '')[:200]
            if key not in unique:
                unique[key] = (d, s)

        return [v[0] for v in list(unique.values())[:k]]

    # fallback to standard similarity search
    if hasattr(vectorstore, 'similarity_search'):
        return vectorstore.similarity_search(query, k=k)

    # last resort: try a generic search call
    try:
        return vectorstore.search(query)[:k]
    except Exception as exc:
        raise ValueError('Vectorstore does not support known similarity search APIs') from exc
