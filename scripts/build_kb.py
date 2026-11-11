"""Constrói a base de conhecimento e os índices.

Uso:
    python scripts/build_kb.py                 # documentos + TF-IDF + embeddings (FAISS)
    python scripts/build_kb.py --no-dense      # só TF-IDF (rápido, sem baixar modelo)
    python scripts/build_kb.py --model intfloat/multilingual-e5-large
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from voc.config import settings  # noqa: E402
from voc.index import DenseIndex, TfidfIndex  # noqa: E402
from voc.prep import build_documents, load_raw, save_documents  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-dense", action="store_true", help="não gera embeddings")
    ap.add_argument("--model", default=settings.embedding_model)
    args = ap.parse_args()

    t0 = time.time()
    print("1/3 Preparando documentos…")
    df, stats = build_documents(load_raw())
    save_documents(df, stats)

    settings.index_dir.mkdir(parents=True, exist_ok=True)
    print("2/3 Índice lexical (TF-IDF 1-2 gramas)…")
    tf = TfidfIndex.build(df["text_fold"].tolist())
    tf.save(settings.index_dir)
    print(f"  vocabulário: {len(tf.vectorizer.vocabulary_):,} termos")

    if args.no_dense:
        print("3/3 Embeddings pulados (--no-dense).")
    else:
        print(f"3/3 Embeddings com {args.model} (primeira execução baixa o modelo)…")
        try:
            DenseIndex.build(df["text"].tolist(), args.model).save(settings.index_dir)
        except Exception as exc:
            print(f"  [aviso] não foi possível gerar embeddings: {exc}\n"
                  "  O sistema funcionará só com TF-IDF. Verifique internet/instalação do fastembed.")
    print(f"Pronto em {time.time() - t0:.0f}s. Documentos: {len(df):,}")


if __name__ == "__main__":
    main()
