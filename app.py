"""Interface web: streamlit run app.py"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from voc.pipeline import VoCRAG  # noqa: E402

st.set_page_config(page_title="Voice of Customer · RAG Olist", layout="wide")

STATUS = {
    "ok": ("✅", "Resposta fundamentada"),
    "evidencia_insuficiente": ("⚠️", "Evidências insuficientes"),
    "fora_do_escopo": ("🚫", "Fora do escopo da base"),
    "sem_dados_no_filtro": ("∅", "Sem avaliações no filtro"),
}
EXEMPLOS = [
    "Quais são os principais problemas relatados pelos clientes em suas avaliações?",
    "O que os clientes relatam sobre problemas relacionados à entrega?",
    "Quais aspectos da experiência de compra são mais elogiados pelos clientes?",
    "Quais padrões podem ser identificados nas avaliações de clientes insatisfeitos?",
    "Quais avaliações sustentam a conclusão de que existem problemas recorrentes relacionados ao prazo de entrega?",
    "O que os clientes mais elogiam em produtos de beleza e saúde?",
    "Qual é a capital da França?",
]


@st.cache_resource(show_spinner="Carregando base de conhecimento e índices…")
def load(generator: str) -> VoCRAG:
    return VoCRAG(generator=generator)


with st.sidebar:
    st.header("Configuração")
    generator = st.selectbox("Geração", ["auto", "anthropic", "openai", "extractive"],
                             help="auto: Anthropic se houver ANTHROPIC_API_KEY, senão OpenAI-compatível, senão extrativo")
    rag = load(generator)
    st.caption(f"Busca: {'+'.join(b for b, i in [('tfidf', rag.retriever.tfidf), ('dense', rag.retriever.dense)] if i)} · "
               f"Gerador: {rag.generator.name} · {len(rag.docs):,} avaliações")
    st.header("Filtros (opcional)")
    st.caption("Vazio = o sistema infere da pergunta.")
    use_intent = st.checkbox("Inferir nota pela intenção (reclamação → 1–3, elogio → 4–5)", True)
    notas = st.select_slider("Nota", options=[1, 2, 3, 4, 5], value=(1, 5))
    cats = st.multiselect("Categoria", rag.retriever.categories)
    anos = st.multiselect("Ano", [2016, 2017, 2018])
    atraso = st.selectbox("Entrega", ["(qualquer)", "entregue com atraso", "entregue no prazo"])

st.title("Voice of Customer Intelligence")
st.caption("RAG sobre avaliações de clientes do Brazilian E-Commerce Public Dataset by Olist")

ex = st.selectbox("Exemplos", [""] + EXEMPLOS)
q = st.text_input("Pergunta", value=ex)

if st.button("Perguntar", type="primary") and q.strip():
    overrides = {
        "score_range": None if notas == (1, 5) else tuple(notas),
        "categories": cats or None,
        "years": anos or None,
        "delivered_late": {"entregue com atraso": True, "entregue no prazo": False}.get(atraso),
    }
    with st.spinner("Recuperando avaliações e gerando resposta…"):
        a = rag.ask(q, overrides=overrides, use_intent_filter=use_intent)

    icon, label = STATUS.get(a.status, ("", a.status))
    st.subheader(f"{icon} {label}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avaliações no recorte", f"{a.n_filtered:,}")
    c2.metric("Evidências relevantes", a.n_relevant)
    c3.metric("Avaliações que sustentam", a.n_supporting)
    c4.metric("Cobertura dos termos", f"{a.coverage:.0%}")
    st.caption(f"Filtros: {a.filters} · Busca: {' + '.join(a.backends)} · Geração: {a.generator}")
    for n in a.plan_notes:
        st.caption(f"ℹ️ {n}")
    for w in a.warnings:
        st.warning(w)
    st.markdown(a.answer)

    evs = a.cited_evidences or a.evidences
    st.subheader("Evidências" + (" citadas" if a.cited_evidences else " recuperadas"))
    for e in evs:
        with st.expander(f"[{e.ref}] ⭐{e.score} · {e.category} · {e.review_date}"):
            st.write(f"“{e.text}”")
            st.caption(f"review_id {e.review_id} · pedido {e.order_id} · temas: {', '.join(e.themes) or '—'} · "
                       f"lexical={e.lexical_score} · denso={e.dense_score} · atraso={e.delay_days}")

    if a.stats.get("n"):
        with st.expander("Estatísticas do recorte (todas as avaliações filtradas)"):
            s = a.stats
            st.bar_chart(pd.Series(s["temas_pct"], name="% das avaliações"))
            st.json({k: v for k, v in s.items() if k != "temas_pct"})
