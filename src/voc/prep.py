"""Construção da base de conhecimento: seleção, limpeza, metadados e documentos."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import settings
from .text import clean_text, detect_themes, fold

RAW_FILES = {
    "reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "translation": "product_category_name_translation.csv",
}


def _parse_dt(s: pd.Series) -> pd.Series:
    """Datas aparecem em ISO (Kaggle) ou M/D/AAAA (CSV re-salvo no Excel). Aceita as duas."""
    iso = pd.to_datetime(s, format="%Y-%m-%d %H:%M:%S", errors="coerce")
    us = pd.to_datetime(s, format="%m/%d/%Y %H:%M", errors="coerce")
    return iso.fillna(us)


def _read_translation(path: Path) -> dict[str, str]:
    # Algumas cópias do arquivo vêm com a linha inteira entre aspas: "a,b"
    out = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines()[1:]:
        line = line.strip().strip('"')
        if "," in line:
            pt, en = line.split(",", 1)
            out[pt.strip().strip('"')] = en.strip().strip('"')
    return out


def load_raw(raw_dir: Path | None = None) -> dict[str, pd.DataFrame | dict]:
    raw_dir = raw_dir or settings.raw_dir
    missing = [f for f in RAW_FILES.values() if not (raw_dir / f).exists()]
    if missing:
        raise FileNotFoundError(
            f"Arquivos ausentes em {raw_dir}: {missing}. Veja README (seção Dados)."
        )
    return {
        "reviews": pd.read_csv(raw_dir / RAW_FILES["reviews"]),
        "orders": pd.read_csv(raw_dir / RAW_FILES["orders"]),
        "items": pd.read_csv(raw_dir / RAW_FILES["items"]),
        "products": pd.read_csv(raw_dir / RAW_FILES["products"]),
        "translation": _read_translation(raw_dir / RAW_FILES["translation"]),
    }


def build_documents(raw: dict, verbose: bool = True) -> tuple[pd.DataFrame, dict]:
    stats: dict = {}
    rv = raw["reviews"].copy()
    stats["reviews_total"] = len(rv)

    # 1) Limpeza dos campos textuais (título + mensagem)
    rv["title"] = rv["review_comment_title"].map(clean_text)
    rv["message"] = rv["review_comment_message"].map(clean_text)
    stats["sem_mensagem"] = int((rv["message"] == "").sum())
    stats["sem_titulo"] = int((rv["title"] == "").sum())

    def _join(t: str, m: str) -> str:
        if t and m:
            return m if fold(t) in fold(m) else f"{t}. {m}"
        return t or m

    rv["text"] = [_join(t, m) for t, m in zip(rv["title"], rv["message"])]

    # 2) Seleção: só avaliações com conteúdo textual informativo
    n_words = rv["text"].str.split().str.len().fillna(0)
    keep = (rv["text"].str.len() >= settings.min_chars) & (n_words >= settings.min_words)
    stats["descartadas_texto_curto_ou_vazio"] = int((~keep).sum())
    rv = rv[keep].copy()

    # 3) Duplicatas: mesmo review_id ou mesmo texto no mesmo pedido
    before = len(rv)
    rv = rv.drop_duplicates("review_id")
    rv["_k"] = rv["text"].map(fold)
    rv = rv.drop_duplicates(["order_id", "_k"]).drop(columns="_k")
    stats["duplicatas_removidas"] = before - len(rv)

    # 4) Metadados do pedido (entrega)
    od = raw["orders"].copy()
    for c in [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]:
        od[c] = _parse_dt(od[c])
    od["delivery_days"] = (
        od["order_delivered_customer_date"] - od["order_purchase_timestamp"]
    ).dt.days
    od["delay_days"] = (
        od["order_delivered_customer_date"] - od["order_estimated_delivery_date"]
    ).dt.days
    od["delivered_late"] = np.where(
        od["order_delivered_customer_date"].isna(), np.nan, (od["delay_days"] > 0).astype(float)
    )
    od = od[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "delivery_days",
            "delay_days",
            "delivered_late",
        ]
    ]

    # 5) Categoria do produto (pedido com vários itens: categoria mais frequente; empate -> 1º item)
    it = raw["items"][["order_id", "order_item_id", "product_id", "price", "freight_value"]]
    pr = raw["products"][["product_id", "product_category_name"]]
    it = it.merge(pr, on="product_id", how="left")
    it["product_category_name"] = it["product_category_name"].fillna("desconhecida")
    agg = it.groupby("order_id").agg(
        n_items=("order_item_id", "count"),
        order_value=("price", "sum"),
        freight_value=("freight_value", "sum"),
        category=("product_category_name", lambda s: s.value_counts().index[0]),
    )
    tr = raw["translation"]
    agg["category_en"] = agg["category"].map(lambda c: tr.get(c, c))
    agg = agg.reset_index()

    df = rv.merge(od, on="order_id", how="left").merge(agg, on="order_id", how="left")
    stats["sem_pedido"] = int(df["order_status"].isna().sum())
    stats["sem_categoria"] = int(df["category"].isna().sum())
    df["category"] = df["category"].fillna("desconhecida")
    df["category_en"] = df["category_en"].fillna("unknown")
    df["order_status"] = df["order_status"].fillna("desconhecido")

    # 6) Campos derivados
    df["review_date"] = _parse_dt(df["review_creation_date"])
    df["year_month"] = df["review_date"].dt.strftime("%Y-%m")
    df["year"] = df["review_date"].dt.year.astype("Int64")
    df["sentiment"] = pd.cut(
        df["review_score"], bins=[0, 2, 3, 5], labels=["negativa", "neutra", "positiva"]
    ).astype(str)
    df["text_fold"] = df["text"].map(fold)
    df["themes"] = df["text_fold"].map(lambda t: "|".join(detect_themes(t)))

    df = df.reset_index(drop=True)
    df["doc_id"] = np.arange(len(df))
    cols = [
        "doc_id", "review_id", "order_id", "review_score", "sentiment", "title", "message", "text",
        "text_fold", "themes", "review_date", "year_month", "year", "order_status",
        "order_purchase_timestamp", "delivery_days", "delay_days", "delivered_late", "category",
        "category_en", "n_items", "order_value", "freight_value",
    ]
    df = df[cols]
    stats["documentos_finais"] = len(df)
    stats["distribuicao_notas"] = {int(k): int(v) for k, v in df["review_score"].value_counts().sort_index().items()}
    stats["pct_entregue_atrasado"] = round(float(df["delivered_late"].mean() * 100), 2)
    if verbose:
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    return df, stats


def save_documents(df: pd.DataFrame, stats: dict) -> None:
    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(settings.docs_path, index=False, compression="gzip")
    (settings.processed_dir / "build_stats.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def load_documents() -> pd.DataFrame:
    df = pd.read_csv(settings.docs_path, keep_default_na=True)
    for c in ["title", "message", "text", "text_fold", "themes"]:
        df[c] = df[c].fillna("").astype(str)
    df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
    df["year"] = df["year"].astype("Int64")
    return df
