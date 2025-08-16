import sys
import types
from types import SimpleNamespace

import pytest

from easy_rag_pipeline.adapters.raganything_adapter import parse_with_raganything


def make_node(id='n1', title='T', caption='C', text='body', page=1, modalities=None):
    return SimpleNamespace(id=id, title=title, caption=caption, text=text, page=page, modalities=modalities or [])


def test_parse_with_RAGAnything_entrypoint(monkeypatch):
    fake_module = types.ModuleType('raganything')

    class FakeRag:
        def __init__(self, config=None):
            self.config = config

        def parse(self, source_path):
            return SimpleNamespace(nodes=[make_node()])

    fake_module.RAGAnything = FakeRag
    monkeypatch.setitem(sys.modules, 'raganything', fake_module)

    res = parse_with_raganything('doc.pdf', config={'x': 1})
    assert isinstance(res, list)
    assert len(res) == 1
    d = res[0]
    assert hasattr(d, 'page_content')
    assert 'Title:' in d.page_content
    assert d.metadata['node_id'] == 'n1'
    assert d.metadata['source'] == 'doc.pdf'


def test_parse_with_parse_function_entrypoint(monkeypatch):
    fake_module = types.ModuleType('raganything')

    def fake_parse(source_path, config=None):
        return SimpleNamespace(nodes=[make_node(id='n2', title='Title2', caption=None, text='txt', page=2, modalities=['image'])])

    fake_module.parse = fake_parse
    monkeypatch.setitem(sys.modules, 'raganything', fake_module)

    res = parse_with_raganything('file.txt', config=None)
    assert len(res) == 1
    d = res[0]
    assert 'Title: Title2' in d.page_content
    assert d.metadata['node_id'] == 'n2'
    assert d.metadata['modalities'] == ['image']


def test_missing_raganything_raises(monkeypatch):
    # Ensure module is not present
    monkeypatch.delitem(sys.modules, 'raganything', raising=False)
    with pytest.raises(ImportError):
        parse_with_raganything('nope')
