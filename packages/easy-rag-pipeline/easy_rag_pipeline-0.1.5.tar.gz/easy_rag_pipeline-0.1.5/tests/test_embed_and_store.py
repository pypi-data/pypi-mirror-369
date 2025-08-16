import pytest

from easy_rag_pipeline.embed import get_embedding_function


def test_simple_embedding_returns_fixed_dim_and_stable_values():
    emb = get_embedding_function({'provider': 'simple', 'dim': 16})
    v1 = emb.embed_query('hello')
    v2 = emb.embed_query('hello')
    assert isinstance(v1, list)
    assert len(v1) == 16
    assert v1 == v2  # deterministic


def test_unsupported_provider_raises():
    with pytest.raises(ValueError):
        get_embedding_function({'provider': 'nope'})


def test_create_vector_store_nodeid_map_and_graph(monkeypatch):
    # Create fake chunk objects with the minimal attributes required by FAISS.from_documents
    class Chunk:
        def __init__(self, page_content, metadata):
            self.page_content = page_content
            self.metadata = metadata

    chunks = [
        Chunk('a', {'node_id': 'n1'}),
        Chunk('b', {'node_id': 'n2', 'belongs_to': 'n1'}),
    ]

    # Monkeypatch FAISS.from_documents to return a simple object we can inspect
    class FakeFAISS:
        def __init__(self):
            self._docs = None

        @classmethod
        def from_documents(cls, documents, embedding):
            inst = cls()
            inst._docs = documents
            return inst

    import easy_rag_pipeline.store as store_mod

    monkeypatch.setattr(store_mod, 'FAISS', FakeFAISS)

    emb = get_embedding_function({'provider': 'simple', 'dim': 8})
    db = store_mod.create_vector_store(chunks, emb, {'provider': 'faiss'})
    assert hasattr(db, 'nodeid_map')
    assert 'n1' in db.nodeid_map
    assert 'n2' in db.nodeid_map
    assert hasattr(db, 'graph')
    # n1 and n2 should be connected due to belongs_to
    assert db.graph.get('n1') and 'n2' in db.graph.get('n1')
