from types import SimpleNamespace

from easy_rag_pipeline.retrieve import retrieve_documents


class Doc:
    def __init__(self, text, metadata=None):
        self.page_content = text
        self.metadata = metadata or {}


def test_mmr_selects_diverse_docs():
    # create fake vectorstore with similarity_search_with_relevance_scores
    docs = [Doc('A content'), Doc('B content'), Doc('A long content')]
    scores = [(docs[0], 0.9), (docs[1], 0.8), (docs[2], 0.7)]

    class FakeVS:
        def similarity_search_with_relevance_scores(self, query, k=None):
            return scores[:k]

    vs = FakeVS()
    res = retrieve_documents('q', vs, k=2, use_mmr=True, fetch_k=3)
    # should pick top scored doc and a non-overlapping doc (B)
    assert len(res) == 2
    assert res[0].page_content == 'A content'
    assert any(r.page_content == 'B content' for r in res)


def test_graph_expansion_combines_scores_and_dedupes():
    # Create fake node docs
    d1 = Doc('doc1', metadata={'node_id': 'n1', 'source': 's1'})
    d2 = Doc('doc2', metadata={'node_id': 'n2', 'source': 's2'})

    # Fake vectorstore with graph and nodeid_map
    class FakeVS:
        def __init__(self):
            self.graph = {'n1': ['n2'], 'n2': ['n1']}
            self.nodeid_map = {'n1': [d1], 'n2': [d2]}

        def similarity_search_with_relevance_scores(self, query, k=None):
            # return candidate doc for n1 only
            return [(d1, 0.9)]

    vs = FakeVS()
    out = retrieve_documents('q', vs, k=2, use_graph=True, fetch_k=2, graph_alpha=0.8, graph_beta=0.2)
    # should include both d1 and d2 due to expansion
    assert any(o.page_content == 'doc1' for o in out)
    assert any(o.page_content == 'doc2' for o in out)
