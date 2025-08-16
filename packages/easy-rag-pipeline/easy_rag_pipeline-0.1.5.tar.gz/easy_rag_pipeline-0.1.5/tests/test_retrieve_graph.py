import pytest
import os
import sys

# Add root project directory to path so tests can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from easy_rag_pipeline.retrieve import retrieve_documents


class FakeDoc:
    def __init__(self, text, metadata=None):
        self.page_content = text
        self.metadata = metadata or {}


class FakeVectorStore:
    def __init__(self, docs_by_node, graph):
        # docs_by_node: dict node_id -> list[FakeDoc]
        self.nodeid_map = docs_by_node
        self.graph = graph
        # flatten docs for similarity_search
        self._all_docs = []
        for node, docs in docs_by_node.items():
            for d in docs:
                self._all_docs.append(d)

    def similarity_search(self, query, k=5):
        # naive: return first k docs
        return self._all_docs[:k]

    def similarity_search_with_relevance_scores(self, query, k=10):
        # return each doc with descending fake scores
        results = []
        score = float(k)
        for d in self._all_docs[:k]:
            results.append((d, score))
            score -= 1.0
        return results


def test_vector_graph_fusion_expands_neighbors():
    # node A has docA, node B neighbor has docB, node C isolated has docC
    docA = FakeDoc('A text', metadata={'node_id': 'A'})
    docB = FakeDoc('B text', metadata={'node_id': 'B', 'belongs_to': 'A'})
    docC = FakeDoc('C text', metadata={'node_id': 'C'})

    docs_by_node = {'A': [docA], 'B': [docB], 'C': [docC]}
    graph = {'A': ['B'], 'B': ['A'], 'C': []}

    vs = FakeVectorStore(docs_by_node, graph)

    results = retrieve_documents('query', vs, k=3, use_graph=True, fetch_k=3)

    # Expect that docs from node A and B are returned (expanded), C may be lower ranked
    returned_nodes = {d.metadata.get('node_id') for d in results}
    assert 'A' in returned_nodes
    assert 'B' in returned_nodes
