"""Baixa o dataset da Olist do Kaggle para data/raw/.

Opção 1 (automática): pip install kagglehub  e  python scripts/download_data.py
   (na primeira vez o kagglehub pede login — crie um token em kaggle.com > Settings > API)
Opção 2 (manual): baixe o zip em https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
   e extraia os CSVs em data/raw/.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from voc.prep import RAW_FILES  # noqa: E402

dest = ROOT / "data" / "raw"
dest.mkdir(parents=True, exist_ok=True)

import kagglehub  # noqa: E402

src = Path(kagglehub.dataset_download("olistbr/brazilian-ecommerce"))
for name in RAW_FILES.values():
    hit = next(src.rglob(name), None)
    if hit is None:
        sys.exit(f"Arquivo {name} não encontrado em {src}")
    shutil.copy(hit, dest / name)
    print("ok", name)
print(f"Dados em {dest}")
