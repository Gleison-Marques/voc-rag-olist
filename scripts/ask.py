"""Pergunta pela linha de comando.

    python scripts/ask.py "O que os clientes relatam sobre problemas de entrega?"
    python scripts/ask.py --json "Quais os principais problemas nas avaliações com nota baixa?"
    python scripts/ask.py            # modo interativo
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from voc.pipeline import Answer, VoCRAG  # noqa: E402


def render(a: Answer, show_all: bool = False) -> str:
    out = [
        "=" * 90,
        f"PERGUNTA: {a.question}",
        f"status: {a.status} | filtros: {a.filters} | recorte: {a.n_filtered} avaliações | "
        f"relevantes: {a.n_relevant} | busca: {'+'.join(a.backends)} | geração: {a.generator}",
    ]
    out += [f"nota do planejador: {n}" for n in a.plan_notes]
    out += [f"⚠ {w}" for w in a.warnings]
    out += ["-" * 90, a.answer, "-" * 90]
    evs = a.evidences if (show_all or not a.cited_refs) else a.cited_evidences
    out.append("EVIDÊNCIAS" + (" CITADAS" if a.cited_refs and not show_all else ""))
    for e in evs:
        out.append(
            f"[{e.ref}] nota {e.score} | {e.category} | {e.review_date} | review_id={e.review_id} "
            f"| lex={e.lexical_score} dense={e.dense_score}\n     \"{e.text}\""
        )
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="*")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true", help="mostrar todas as evidências recuperadas")
    ap.add_argument("--backend", default=None, help="hybrid | dense | tfidf")
    ap.add_argument("--generator", default=None, help="auto | anthropic | openai | extractive")
    args = ap.parse_args()

    rag = VoCRAG(backend=args.backend, generator=args.generator)
    questions = [" ".join(args.question)] if args.question else None
    while True:
        q = questions.pop() if questions else input("\nPergunta (enter para sair): ").strip()
        if not q:
            break
        a = rag.ask(q)
        print(json.dumps(a.to_dict(), ensure_ascii=False, indent=2, default=str) if args.json else render(a, args.all))
        if args.question:
            break


if __name__ == "__main__":
    main()
