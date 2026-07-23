"""
AcadEval Domain Taxonomy Loader
=================================
Provides fast, cached loading of the taxonomy into dicts / DataFrames.
Used by Module 4 (Domain Classification) and Module 5 (Similarity Detection).
"""

import json
import logging
from functools import lru_cache
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

TAXONOMY_DIR = Path(__file__).parent
CSV_PATH     = TAXONOMY_DIR / "AcadEval_DomainTaxonomy.csv"
JSON_PATH    = TAXONOMY_DIR / "AcadEval_DomainTaxonomy.json"


@lru_cache(maxsize=1)
def load_dataframe() -> pd.DataFrame:
    """Return the full taxonomy as a cached DataFrame."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Taxonomy CSV not found at {CSV_PATH}. "
            "Run taxonomy_generator.py first."
        )
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    log.info("Taxonomy loaded: %d rows, %d domains", len(df), df["Domain"].nunique())
    return df


@lru_cache(maxsize=1)
def load_json() -> list[dict]:
    """Return the taxonomy as a list of dicts (from JSON)."""
    if not JSON_PATH.exists():
        # Fall back: build from CSV
        return load_dataframe().to_dict(orient="records")
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def get_domains() -> list[str]:
    """Sorted list of unique top-level domains."""
    return sorted(load_dataframe()["Domain"].unique().tolist())


def get_sub_domains(domain: str) -> list[str]:
    """Sub-domains for a given domain."""
    df = load_dataframe()
    return sorted(
        df[df["Domain"].str.lower() == domain.lower()]["Sub_Domain"].unique().tolist()
    )


def get_topics(domain: str, sub_domain: str | None = None) -> list[str]:
    """Topics optionally filtered by domain and sub-domain."""
    df = load_dataframe()
    mask = df["Domain"].str.lower() == domain.lower()
    if sub_domain:
        mask &= df["Sub_Domain"].str.lower() == sub_domain.lower()
    return sorted(df[mask]["Topic"].tolist())


def get_keywords_for_domain(domain: str) -> set[str]:
    """Union of common and related keywords across all topics in a domain."""
    df = load_dataframe()
    sub = df[df["Domain"].str.lower() == domain.lower()]
    keywords: set[str] = set()
    for col in ("Common_Keywords", "Related_Keywords"):
        for cell in sub[col].dropna():
            keywords.update(k.strip().lower() for k in cell.split(",") if k.strip())
    return keywords


def get_row_by_id(taxonomy_id: str) -> dict | None:
    """Retrieve a single row by Taxonomy_ID."""
    df = load_dataframe()
    row = df[df["Taxonomy_ID"] == taxonomy_id]
    if row.empty:
        return None
    return row.iloc[0].to_dict()


def get_all_keywords() -> dict[str, list[str]]:
    """
    Returns a dict mapping domain -> list of lowercase keywords.
    Useful as a keyword-index for domain classification.
    """
    df = load_dataframe()
    index: dict[str, set[str]] = {}
    for _, row in df.iterrows():
        domain = row["Domain"]
        if domain not in index:
            index[domain] = set()
        for col in ("Common_Keywords", "Related_Keywords"):
            cell = str(row.get(col, ""))
            index[domain].update(k.strip().lower() for k in cell.split(",") if k.strip())
    return {d: sorted(kws) for d, kws in index.items()}


def get_domain_metadata() -> pd.DataFrame:
    """Summary table with one row per domain."""
    df = load_dataframe()
    return (
        df.groupby("Domain")
        .agg(
            Sub_Domains=("Sub_Domain", "nunique"),
            Topics=("Topic", "nunique"),
            Emerging=("Emerging_Topic", lambda x: (x == "Yes").sum()),
        )
        .reset_index()
        .sort_values("Domain")
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Domains:", get_domains()[:5], "…")
    print("Sub-domains (AI):", get_sub_domains("Artificial Intelligence"))
    print("Topics (AI, Expert Systems):", get_topics("Artificial Intelligence", "Expert Systems"))
    print("\nDomain metadata:")
    print(get_domain_metadata().to_string(index=False))
