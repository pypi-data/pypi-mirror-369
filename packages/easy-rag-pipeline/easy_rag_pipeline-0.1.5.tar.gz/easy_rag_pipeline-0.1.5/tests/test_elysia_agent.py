import asyncio


def test_local_retrieve_tool_monkeypatch(monkeypatch):
    """Run the async local_retrieve_tool via asyncio.run so pytest-asyncio is not required."""
    from easy_rag_pipeline.agents.elysia_agent import local_retrieve_tool

    # create fake doc objects
    class FakeDoc:
        def __init__(self, text, score, meta=None):
            self.page_content = text
            self.metadata = {"score": score, **(meta or {})}

    # monkeypatch the retrieval function used by the wrapper
    import easy_rag_pipeline
    from types import SimpleNamespace

    fake_list = [
        FakeDoc("foo", 0.9, {"source": "doc1"}),
        FakeDoc("bar", 0.5, {"source": "doc2"}),
    ]

    monkeypatch.setattr(
        easy_rag_pipeline,
        "retrieve",
        SimpleNamespace(retrieve_documents=lambda q, v, k, g: fake_list),
    )

    out = asyncio.run(local_retrieve_tool("query", k=2, vectorstore=None, use_graph=False))
    assert "chunks" in out and isinstance(out["chunks"], list)
    assert out["retrieval_confidence"] == 0.9
    assert out["chunks"][0]["text"] == "foo"


def test_generate_tool_monkeypatch(monkeypatch):
    """Run the async generate_tool via asyncio.run so pytest-asyncio is not required."""
    from easy_rag_pipeline.agents.elysia_agent import generate_tool

    # monkeypatch easy_rag_pipeline.generate.generate_answer
    import easy_rag_pipeline

    def fake_generate(query, chunks, llm_config):
        return f"ANSWER to {query} with {len(chunks)} chunks"

    from types import SimpleNamespace

    monkeypatch.setattr(
        easy_rag_pipeline,
        "generate",
        SimpleNamespace(generate_answer=fake_generate),
    )

    chunks = [{"text": "a", "meta": {"source": "s1"}}, {"text": "b", "meta": {"source": "s2"}}]
    out = asyncio.run(generate_tool("q", chunks))
    assert "answer" in out and "sources" in out
    assert out["answer"].startswith("ANSWER to q")
    assert out["sources"] == ["s1", "s2"]
