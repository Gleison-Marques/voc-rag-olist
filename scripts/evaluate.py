"""Avaliação do pipeline: recusa correta, rastreabilidade das citações e precisão temática.

    python scripts/evaluate.py                    # modo extrativo (determinístico, sem custo)
    python scripts/evaluate.py --generator auto   # usa o LLM configurado
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from voc.pipeline import VoCRAG  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generator", default="extractive")
    ap.add_argument("--backend", default=None)
    ap.add_argument("--out", default=str(ROOT / "docs" / "eval_results.json"))
    args = ap.parse_args()

    cases = json.loads((ROOT / "docs" / "eval_questions.json").read_text(encoding="utf-8"))
    rag = VoCRAG(backend=args.backend, generator=args.generator)
    rows, ok_status, prec, cite_ok = [], 0, [], []
    for c in cases:
        a = rag.ask(c["q"])
        refused = a.status != "ok"
        hit = (c["expect"] == "refuse") == refused
        ok_status += hit
        p_theme = None
        if a.status == "ok" and c.get("themes"):
            evs = a.evidences
            p_theme = sum(bool(set(e.themes) & set(c["themes"])) for e in evs) / max(len(evs), 1)
            prec.append(p_theme)
        if a.status == "ok":
            valid = {e.ref for e in a.evidences}
            cite_ok.append(bool(a.cited_refs) and set(a.cited_refs) <= valid)
        rows.append({
            "pergunta": c["q"], "esperado": c["expect"], "status": a.status, "acertou": hit,
            "filtros": a.filters, "recorte": a.n_filtered, "relevantes": a.n_relevant,
            "cobertura": a.coverage, "termos_ausentes": a.missing_terms,
            "precisao_tematica": None if p_theme is None else round(p_theme, 2),
            "citacoes": a.cited_refs, "avisos": a.warnings,
        })
        print(f"{'✔' if hit else '✘'} [{a.status:24}] cov={a.coverage:.2f} rel={a.n_relevant:2} "
              f"prec={'-' if p_theme is None else f'{p_theme:.2f}'}  {c['q'][:70]}")

    summary = {
        "casos": len(cases),
        "acuracia_decisao_responder_recusar": round(ok_status / len(cases), 3),
        "precisao_tematica_media@k": round(sum(prec) / len(prec), 3) if prec else None,
        "respostas_com_citacoes_validas": round(sum(cite_ok) / len(cite_ok), 3) if cite_ok else None,
        "backends": rag.retriever.tfidf and "tfidf" or "", "gerador": rag.generator.name,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    Path(args.out).write_text(json.dumps({"resumo": summary, "casos": rows}, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
