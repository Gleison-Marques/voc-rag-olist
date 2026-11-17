from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except Exception:  # pragma: no cover
    pass


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


@dataclass
class Settings:
    raw_dir: Path = ROOT / "data" / "raw"
    processed_dir: Path = ROOT / "data" / "processed"
    index_dir: Path = ROOT / "data" / "index"

    min_chars: int = int(_env("VOC_MIN_CHARS", "10"))
    min_words: int = int(_env("VOC_MIN_WORDS", "2"))

    # backend: "hybrid" (denso + lexical, RRF), "dense" ou "tfidf"
    backend: str = _env("VOC_BACKEND", "hybrid")
    embedding_model: str = _env(
        "VOC_EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    candidates: int = int(_env("VOC_CANDIDATES", "40"))  # recuperados antes do rerank/diversidade
    top_k: int = int(_env("VOC_TOP_K", "12"))  # avaliações enviadas ao LLM
    rrf_k: int = 60

    min_evidence: int = int(_env("VOC_MIN_EVIDENCE", "3"))
    tfidf_min_score: float = float(_env("VOC_TFIDF_MIN_SCORE", "0.12"))
    dense_min_score: float = float(_env("VOC_DENSE_MIN_SCORE", "0.45"))
    min_coverage: float = float(_env("VOC_MIN_COVERAGE", "0.6"))  # termos de assunto cobertos

    # provider: "anthropic", "openai" (qualquer API compatível: OpenAI, Ollama, Groq...) ou "extractive"
    llm_provider: str = _env("VOC_LLM_PROVIDER", "auto")
    llm_model: str = _env("VOC_LLM_MODEL", "")
    llm_base_url: str = _env("VOC_LLM_BASE_URL", "")
    max_review_chars: int = 400

    extra: dict = field(default_factory=dict)

    @property
    def docs_path(self) -> Path:
        return self.processed_dir / "reviews_docs.csv.gz"


settings = Settings()
