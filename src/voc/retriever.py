"""Recuperação híbrida com filtros de metadados, fusão RRF e remoção de redundância."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .config import settings
from .index import DenseIndex, TfidfIndex
from .query import QueryPlan
from .text import THEMES

POS_THEMES = {"entrega_rapida", "satisfacao"}
NEG_THEMES = {"entrega_atraso", "nao_recebido", "produto_divergente", "troca_reembolso"}


def rerank_factor(themes: list[str], n_words: int, p: QueryPlan) -> float:
    """Ajuste leve sobre a fusão: alinhamento de tema e de polaridade com a pergunta."""
    f, ts = 1.0, set(themes)
    if p.target_themes and ts & set(p.target_themes):
        f *= 1.3
    if p.intent == "negativa" and ts and ts <= POS_THEMES:
        f *= 0.6  # "entrega sem problemas" não é evidência de problema
    if p.intent == "positiva" and ts & NEG_THEMES:
        f *= 0.6
    if n_words < 4:
        f *= 0.8  # textos muito curtos carregam pouca informação
    return f


@dataclass
class Evidence:
    ref: str  # R1, R2...
    doc_id: int
    review_id: str
    order_id: str
    score: int
    text: str
    category: str
    review_date: str
    delay_days: float | None
    themes: list[str]
    lexical_score: float = 0.0
    dense_score: float = 0.0
    fused_score: float = 0.0
    relevant: bool = False
    similar_count: int = 1  # quantos textos idênticos (outros clientes) foram agrupados

    def as_context_line(self, max_chars: int) -> str:
        t = self.text if len(self.text) <= max_chars else self.text[:max_chars].rsplit(" ", 1)[0] + "…"
        atraso = ""
        if self.delay_days is not None and not np.isnan(self.delay_days):
            atraso = f" | entrega: {'atrasou ' + str(int(self.delay_days)) + 'd' if self.delay_days > 0 else 'no prazo'}"
        rep = f" | texto repetido por {self.similar_count} clientes" if self.similar_count > 1 else ""
        return f"[{self.ref}] nota {self.score} | {self.category} | {self.review_date}{atraso}{rep}\n\"{t}\""


@dataclass
class Retrieval:
    evidences: list[Evidence]
    n_filtered: int
    stats: dict = field(default_factory=dict)
    backends: list[str] = field(default_factory=list)


class Retriever:
    def __init__(self, docs: pd.DataFrame, tfidf: TfidfIndex | None, dense: DenseIndex | None):
        if tfidf is None and dense is None:
            raise ValueError("Nenhum índice carregado. Rode scripts/build_kb.py")
        self.docs = docs
        self.tfidf = tfidf
        self.dense = dense
        self.categories = sorted(docs["category"].dropna().unique().tolist())
        self._theme_matrix = {k: docs["themes"].str.contains(rf"\b{k}\b", regex=True).to_numpy() for k in THEMES}

    @classmethod
    def load(cls, docs: pd.DataFrame, backend: str | None = None) -> "Retriever":
        backend = backend or settings.backend
        d = settings.index_dir
        tf = TfidfIndex.load(d) if backend in ("tfidf", "hybrid") and TfidfIndex.exists(d) else None
        de = DenseIndex.load(d) if backend in ("dense", "hybrid") and DenseIndex.exists(d) else None
        if backend == "hybrid" and de is None:
            print("[aviso] índice denso não encontrado — usando somente TF-IDF.")
        return cls(docs, tf, de)

    # ------------------------------------------------------------------ filtros
    def mask_for(self, p: QueryPlan) -> np.ndarray:
        d = self.docs
        m = np.ones(len(d), dtype=bool)
        if p.score_range:
            m &= d["review_score"].between(*p.score_range).to_numpy()
        if p.categories:
            m &= d["category"].isin(p.categories).to_numpy()
        if p.years:
            m &= d["year"].isin(p.years).fillna(False).to_numpy(dtype=bool)
        if p.delivered_late is not None:
            m &= (d["delivered_late"] == float(p.delivered_late)).to_numpy()
        return m

    # ------------------------------------------------------------------ estatísticas do recorte
    def slice_stats(self, mask: np.ndarray) -> dict:
        n = int(mask.sum())
        if n == 0:
            return {"n": 0}
        sub = self.docs[mask]
        themes = {
            THEMES[k]["label"]: round(100 * float(v[mask].mean()), 1) for k, v in self._theme_matrix.items()
        }
        return {
            "n": n,
            "notas": {int(k): int(v) for k, v in sub["review_score"].value_counts().sort_index().items()},
            "pct_entregue_com_atraso": round(100 * float(sub["delivered_late"].mean()), 1)
            if sub["delivered_late"].notna().any() else None,
            "temas_pct": dict(sorted(themes.items(), key=lambda x: -x[1])),
            "top_categorias": sub["category"].value_counts().head(5).to_dict(),
        }

    # ------------------------------------------------------------------ busca
    def retrieve(self, p: QueryPlan, top_k: int | None = None) -> Retrieval:
        """Pergunta com assunto específico -> busca híbrida direta.
        Pergunta panorâmica ("principais problemas", "o que mais elogiam") -> busca estratificada
        pelos temas mais frequentes do recorte, para cobrir o panorama e não só a palavra literal."""
        if not p.key_terms and p.intent in ("negativa", "positiva"):
            return self._retrieve_by_themes(p, top_k or settings.top_k)
        return self._retrieve(p, top_k)

    def _retrieve_by_themes(self, p: QueryPlan, top_k: int, n_themes: int = 4) -> Retrieval:
        from dataclasses import replace

        mask = self.mask_for(p)
        stats = self.slice_stats(mask)
        if mask.sum() == 0:
            return Retrieval([], 0, stats, [])
        allowed = (NEG_THEMES | {"qualidade_produto", "atendimento"}) if p.intent == "negativa" \
            else (POS_THEMES | {"qualidade_produto", "atendimento", "embalagem"})
        share = {k: float(v[mask].mean()) for k, v in self._theme_matrix.items() if k in allowed}
        themes = [k for k, v in sorted(share.items(), key=lambda x: -x[1]) if v > 0][:n_themes]
        per = max(2, top_k // max(len(themes), 1))
        out: list[Evidence] = []
        seen: set[int] = set()
        backends: list[str] = []
        for t in themes:
            sub = replace(p, lexical_query=THEMES[t]["expand"], target_themes=[t],
                          question=f"{p.question} ({THEMES[t]['label']})")
            tm = self._theme_matrix[t]
            if p.intent == "positiva" and t not in POS_THEMES:
                tm = tm & self._theme_matrix["satisfacao"]  # "qualidade" elogiada, não defeito
            if p.intent == "negativa" and t in {"qualidade_produto", "atendimento"}:
                tm = tm & ~self._theme_matrix["satisfacao"]
            r = self._retrieve(sub, per * 2, extra_mask=tm)
            backends = r.backends
            for e in [e for e in r.evidences if e.doc_id not in seen][:per]:
                e.relevant = True  # pertence ao tema pelo detector + passou na busca do tema
                seen.add(e.doc_id)
                out.append(e)
        for i, e in enumerate(out[:top_k], 1):
            e.ref = f"R{i}"
        return Retrieval(out[:top_k], int(mask.sum()), stats, backends + ["estratificada-por-tema"])

    def _retrieve(self, p: QueryPlan, top_k: int | None = None,
                  extra_mask: np.ndarray | None = None) -> Retrieval:
        top_k = top_k or settings.top_k
        n_cand = settings.candidates
        mask = self.mask_for(p)
        n_filtered = int(mask.sum())
        stats = self.slice_stats(mask)
        if extra_mask is not None:
            mask = mask & extra_mask
        if n_filtered == 0 or mask.sum() == 0:
            return Retrieval([], 0, stats, [])

        lex, den, backends = {}, {}, []
        if self.tfidf is not None:
            ids, sc = self.tfidf.search(p.lexical_query or p.folded, n_cand, mask)
            lex = dict(zip(ids.tolist(), sc.tolist()))
            backends.append("tfidf")
        if self.dense is not None:
            ids, sc = self.dense.search(p.question, n_cand, mask)
            den = dict(zip(ids.tolist(), sc.tolist()))
            backends.append("dense")

        # Reciprocal Rank Fusion: robusto a escalas diferentes de score
        fused: dict[int, float] = {}
        for ranking in (lex, den):
            for rank, doc in enumerate(sorted(ranking, key=ranking.get, reverse=True)):
                fused[doc] = fused.get(doc, 0.0) + 1.0 / (settings.rrf_k + rank + 1)

        for doc in fused:
            row = self.docs.iloc[doc]
            fused[doc] *= rerank_factor([t for t in row["themes"].split("|") if t],
                                        len(row["text"].split()), p)
        order = sorted(fused, key=fused.get, reverse=True)
        evidences: list[Evidence] = []
        seen: dict[str, Evidence] = {}
        for doc in order:
            row = self.docs.iloc[doc]
            key = row["text_fold"].strip(" .!")
            if key in seen:  # mesmo texto de outro cliente: agrupa (evidência de recorrência)
                seen[key].similar_count += 1
                continue
            ls, ds = lex.get(doc, 0.0), den.get(doc, 0.0)
            ev = Evidence(
                ref="",
                doc_id=int(doc),
                review_id=str(row["review_id"]),
                order_id=str(row["order_id"]),
                score=int(row["review_score"]),
                text=row["text"],
                category=row["category"],
                review_date=str(row["review_date"])[:10],
                delay_days=None if pd.isna(row["delay_days"]) else float(row["delay_days"]),
                themes=[t for t in row["themes"].split("|") if t],
                lexical_score=round(ls, 4),
                dense_score=round(ds, 4),
                fused_score=round(fused[doc], 5),
                relevant=(ls >= settings.tfidf_min_score) or (ds >= settings.dense_min_score),
            )
            seen[key] = ev
            evidences.append(ev)
            if len(evidences) >= top_k:
                break
        # relevantes primeiro, mantendo a ordem da fusão
        evidences.sort(key=lambda e: (not e.relevant, -e.fused_score))
        for i, e in enumerate(evidences, 1):
            e.ref = f"R{i}"
        return Retrieval(evidences, n_filtered, stats, backends)
