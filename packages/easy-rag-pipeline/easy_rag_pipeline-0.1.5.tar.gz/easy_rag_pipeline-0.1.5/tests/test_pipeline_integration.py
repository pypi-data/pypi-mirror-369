import types
from types import SimpleNamespace
import pytest

import easy_rag_pipeline.pipeline as pipeline_mod
import easy_rag_pipeline.generate as generate_mod


class FakeLLM:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, prompt):
        return "FAKE ANSWER"

    def generate(self, *args, **kwargs):
        return "FAKE ANSWER"


def test_simple_rag_pipeline_end_to_end(monkeypatch, tmp_path):
    # Create a small text file
    fp = tmp_path / "doc.txt"
    fp.write_text("Title: T\n\nThis is the content.")

    # Monkeypatch embedding to use simple embeddings
    config = {
        'chunking': {'chunk_size': 1000, 'chunk_overlap': 0},
        'embedding': {'provider': 'simple', 'dim': 8},
        'vector_store': {'provider': 'faiss'},
        'retrieval': {},
        'llm': {'provider': 'openai', 'model': 'gpt', 'api_key': 'x'}
    }

    # Monkeypatch the LLM classes used in generate.py to a simple stub
    monkeypatch.setattr(generate_mod, 'ChatOpenAI', lambda *args, **kwargs: FakeLLM())
    monkeypatch.setattr(generate_mod, 'ChatGroq', lambda *args, **kwargs: FakeLLM())
    monkeypatch.setattr(generate_mod, 'ChatGoogleGenerativeAI', lambda *args, **kwargs: FakeLLM())

    answer = pipeline_mod.simple_rag_pipeline('what is this?', str(fp), 'txt', config)
    assert isinstance(answer, str)


def test_query_rag_pipeline_uses_generate(monkeypatch):
    # Create fake vector store with a single doc
    d = SimpleNamespace(page_content='hello', metadata={'title': 'Hi', 'source': 's'})
    class FakeStore:
        def __init__(self):
            pass
        def similarity_search(self, query, k=None):
            return [d]

    fake_vs = FakeStore()

    # stub generate_answer to confirm it's called with expected args
    called = {}
    def fake_generate(q, docs, llm_conf):
        called['q'] = q
        called['docs'] = docs
        return 'OK'

    monkeypatch.setattr(pipeline_mod, 'generate_answer', fake_generate)

    res = pipeline_mod.query_rag_pipeline('hey', fake_vs, {'llm': {}})
    assert res == 'OK'
    assert called['q'] == 'hey'
    assert isinstance(called['docs'], list)
