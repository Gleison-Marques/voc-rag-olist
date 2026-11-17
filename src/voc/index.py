from __future__ import annotations

import json
import time
from pathlib import Path

import joblib
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

from .config import settings
from .text import STOPWORDS


class TfidfIndex:
    name = "tfidf"

    def __init__(self, vectorizer: TfidfVectorizer, matrix: sparse.csr_matrix):
        self.vectorizer = vectorizer
        self.matrix = matrix  # linhas L2-normalizadas -> produto escalar = cosseno

    @classmethod
    def build(cls, texts_fold: list[str]) -> "TfidfIndex":
        vec = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.5,
            sublinear_tf=True,
            stop_words=sorted(STOPWORDS),
            token_pattern=r"(?u)\b[a-z0-9]{2,}\b",
        )
        return cls(vec, vec.fit_transform(texts_fold).tocsr())

    def search(self, query_fold: str, k: int, mask: np.ndarray | None = None):
        q = self.vectorizer.transform([query_fold])
        if q.nnz == 0:
            return np.array([], dtype=int), np.array([], dtype=float)
        scores = (self.matrix @ q.T).toarray().ravel()
        if mask is not None:
            scores = np.where(mask, scores, -1.0)
        k = min(k, len(scores))
        idx = np.argpartition(-scores, k - 1)[:k]
        idx = idx[np.argsort(-scores[idx])]
        keep = scores[idx] > 0
        return idx[keep], scores[idx][keep]

    def save(self, d: Path) -> None:
        joblib.dump(self.vectorizer, d / "tfidf_vectorizer.joblib")
        sparse.save_npz(d / "tfidf_matrix.npz", self.matrix)

    @classmethod
    def load(cls, d: Path) -> "TfidfIndex":
        return cls(joblib.load(d / "tfidf_vectorizer.joblib"), sparse.load_npz(d / "tfidf_matrix.npz"))

    @staticmethod
    def exists(d: Path) -> bool:
        return (d / "tfidf_matrix.npz").exists()


class Embedder:
    """Embeddings multilíngues via fastembed (ONNX, roda em CPU, sem PyTorch)."""

    def __init__(self, model_name: str):
        from fastembed import TextEmbedding

        self.model_name = model_name
        self.is_e5 = "e5" in model_name.lower()
        self.model = TextEmbedding(model_name=model_name, cache_dir=str(settings.index_dir / "models"))

    def _norm(self, v: np.ndarray) -> np.ndarray:
        v = v.astype("float32")
        return v / np.clip(np.linalg.norm(v, axis=1, keepdims=True), 1e-12, None)

    def passages(self, texts: list[str], batch_size: int = 128) -> np.ndarray:
        if self.is_e5:
            texts = [f"passage: {t}" for t in texts]
        return self._norm(np.array(list(self.model.embed(texts, batch_size=batch_size))))

    def query(self, text: str) -> np.ndarray:
        if self.is_e5:
            text = f"query: {text}"
        return self._norm(np.array(list(self.model.embed([text]))))


class DenseIndex:
    name = "dense"

    def __init__(self, index, embedder: Embedder | None, model_name: str):
        self.index = index
        self._embedder = embedder
        self.model_name = model_name

    @property
    def embedder(self) -> Embedder:
        if self._embedder is None:
            self._embedder = Embedder(self.model_name)
        return self._embedder

    @classmethod
    def build(cls, texts: list[str], model_name: str) -> "DenseIndex":
        import faiss

        emb = Embedder(model_name)
        t0 = time.time()
        vecs = emb.passages(texts)
        print(f"  embeddings: {vecs.shape} em {time.time() - t0:.0f}s")
        index = faiss.IndexFlatIP(vecs.shape[1])  # busca exata por cosseno (vetores normalizados)
        index.add(vecs)
        return cls(index, emb, model_name)

    def search(self, query: str, k: int, mask: np.ndarray | None = None):
        import faiss

        q = self.embedder.query(query)
        params = None
        if mask is not None:
            ids = np.flatnonzero(mask).astype("int64")
            if len(ids) == 0:
                return np.array([], dtype=int), np.array([], dtype=float)
            params = faiss.SearchParameters(sel=faiss.IDSelectorBatch(ids))
            k = min(k, len(ids))
        scores, idx = self.index.search(q, k, params=params)
        idx, scores = idx[0], scores[0]
        ok = idx >= 0
        return idx[ok], scores[ok]

    def save(self, d: Path) -> None:
        import faiss

        faiss.write_index(self.index, str(d / "dense.faiss"))
        (d / "dense_meta.json").write_text(json.dumps({"model": self.model_name}), encoding="utf-8")

    @classmethod
    def load(cls, d: Path) -> "DenseIndex":
        import faiss

        meta = json.loads((d / "dense_meta.json").read_text(encoding="utf-8"))
        return cls(faiss.read_index(str(d / "dense.faiss")), None, meta["model"])

    @staticmethod
    def exists(d: Path) -> bool:
        return (d / "dense.faiss").exists()
