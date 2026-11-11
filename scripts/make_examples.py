"""Gera docs/exemplos.md com perguntas e respostas reais do pipeline."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from voc.pipeline import VoCRAG  # noqa: E402

QUESTIONS = [
    "Quais são os principais problemas relatados pelos clientes em suas avaliações?",
    "O que os clientes relatam sobre problemas relacionados à entrega?",
    "Quais aspectos da experiência de compra são mais elogiados pelos clientes?",
    "Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?",
    "Existem padrões recorrentes nas avaliações relacionadas à qualidade dos produtos?",
    "O que os clientes mais elogiam em produtos de beleza e saúde?",
    "Quais problemas aparecem em móveis de escritório em 2018?",
    "Qual é a capital da França?",
    "O que os clientes acham do aplicativo de realidade virtual da loja?",
    "Quais os problemas relatados em avaliações de 2015?",
]

gen = sys.argv[1] if len(sys.argv) > 1 else None
rag = VoCRAG(generator=gen)
out = ["# Exemplos de perguntas e respostas", "",
       f"Gerado por `scripts/make_examples.py` · busca: {'+'.join(b for b, i in [('tfidf', rag.retriever.tfidf), ('dense', rag.retriever.dense)] if i)}"
       f" · geração: `{rag.generator.name}`", ""]
for q in QUESTIONS:
    a = rag.ask(q)
    out += [f"## {q}", "",
            f"`status={a.status}` · filtros: {a.filters} · recorte: {a.n_filtered:,} avaliações · "
            f"relevantes: {a.n_relevant} · sustentam: {a.n_supporting} · cobertura: {a.coverage:.0%} · "
            f"busca: {' + '.join(a.backends)}", ""]
    out += [f"> ℹ️ {n}" for n in a.plan_notes] + [""] if a.plan_notes else []
    out += [a.answer, "", "<details><summary>Evidências</summary>", ""]
    for e in (a.cited_evidences or a.evidences):
        out.append(f"- **[{e.ref}]** ⭐{e.score} · `{e.category}` · {e.review_date} · `review_id={e.review_id}` — “{e.text}”")
    out += ["", "</details>", ""]
(ROOT / "docs" / "exemplos.md").write_text("\n".join(out), encoding="utf-8")
print("docs/exemplos.md gerado")
