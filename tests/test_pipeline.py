"""Testes do pipeline. Requer a base construída (python scripts/build_kb.py --no-dense)."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from voc import index as idx  # noqa: E402
from voc.config import settings  # noqa: E402
from voc.generator import BaseGenerator  # noqa: E402
from voc.pipeline import VoCRAG  # noqa: E402
from voc.query import plan_query  # noqa: E402
from voc.text import clean_text, detect_themes, fold  # noqa: E402

pytestmark = pytest.mark.skipif(not settings.docs_path.exists(), reason="base não construída")


class FakeLLM(BaseGenerator):
    name = "fake"

    def __init__(self, text):
        self.text = text

    def generate(self, question, evidences, stats, filters):
        return self.text


@pytest.fixture(scope="module")
def rag():
    return VoCRAG(backend="tfidf", generator="extractive")


def test_clean_and_themes():
    assert clean_text("  Muito\n bom!!!!!! ") == "Muito bom!!!"
    assert "entrega_atraso" in detect_themes(fold("O pedido ATRASOU e demorou demais"))
    assert "nao_recebido" in detect_themes(fold("Não recebi o produto"))


def test_plan_filters():
    cats = ["beleza_saude", "moveis_escritorio", "moveis_decoracao"]
    p = plan_query("Quais os problemas em móveis de escritório em 2018 com nota baixa?", cats)
    assert p.score_range == (1, 2) and p.categories == ["moveis_escritorio"] and p.years == [2018]
    p = plan_query("O que mais elogiam?", cats)
    assert p.intent == "positiva" and p.score_range == (4, 5)


@pytest.mark.parametrize("q", [
    "Qual é a capital da França?",
    "Qual a opinião dos clientes sobre a cotação do bitcoin?",
    "O que os clientes acham do aplicativo de realidade virtual da loja?",
])
def test_refuses_without_evidence(rag, q):
    assert rag.ask(q).status in {"fora_do_escopo", "evidencia_insuficiente"}


def test_answer_is_grounded(rag):
    a = rag.ask("O que os clientes relatam sobre problemas relacionados à entrega?")
    assert a.status == "ok" and a.cited_refs
    assert set(a.cited_refs) <= {e.ref for e in a.evidences}
    assert all(e.score <= 3 for e in a.evidences)  # intenção negativa -> notas 1-3


def test_invalid_citations_are_removed(rag):
    rag.generator = FakeLLM("Clientes reclamam de atraso [R1] e de algo inventado [R99].")
    a = rag.ask("O que os clientes relatam sobre atraso na entrega?")
    assert "R99" not in a.answer and a.cited_refs == ["R1"] and a.warnings
    rag.generator = FakeLLM("Resposta sem nenhuma citação.")
    a = rag.ask("O que os clientes relatam sobre atraso na entrega?")
    assert a.cited_refs and any("sem citações" in w for w in a.warnings)
    rag.generator = FakeLLM("EVIDENCIAS_INSUFICIENTES\nAs avaliações não tratam disso.")
    assert rag.ask("O que os clientes relatam sobre atraso na entrega?").status == "evidencia_insuficiente"


class HashEmbedder:
    """Substitui o modelo real (sem download) para testar FAISS + filtros + fusão."""

    model_name, is_e5 = "fake", False

    def __init__(self, *_):
        pass

    def _v(self, texts):
        m = np.zeros((len(texts), 256), dtype="float32")
        for i, t in enumerate(texts):
            for w in fold(t).split():
                m[i, hash(w[:5]) % 256] += 1
        return m / np.clip(np.linalg.norm(m, axis=1, keepdims=True), 1e-9, None)

    def passages(self, texts, batch_size=128):
        return self._v(texts)

    def query(self, text):
        return self._v([text])


def test_dense_index_with_mask(monkeypatch, rag):
    monkeypatch.setattr(idx, "Embedder", HashEmbedder)
    texts = rag.docs["text"].tolist()[:3000]
    dense = idx.DenseIndex.build(texts, "fake")
    mask = np.zeros(len(texts), dtype=bool)
    mask[::2] = True
    ids, scores = dense.search("entrega atrasada", 10, mask)
    assert len(ids) == 10 and all(i % 2 == 0 for i in ids) and np.all(np.diff(scores) <= 1e-6)
