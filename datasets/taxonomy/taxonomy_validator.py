"""
AcadEval Domain Taxonomy Validator
====================================
Validates the generated taxonomy CSV for completeness and integrity.
"""

import json
import sys
from pathlib import Path

import pandas as pd

TAXONOMY_DIR = Path(__file__).parent
REQUIRED_COLUMNS = [
    "Taxonomy_ID", "Domain", "Sub_Domain", "Topic", "Parent_Topic",
    "Description", "Common_Keywords", "Related_Keywords", "Technologies",
    "Algorithms", "Programming_Languages", "Frameworks", "Libraries",
    "Hardware", "Typical_Datasets", "Research_Areas", "Application_Areas",
    "Difficulty_Level", "Industry", "Emerging_Topic", "Trend_Level",
    "Related_Domains", "Source", "Notes",
]
VALID_DIFFICULTY = {"Beginner", "Intermediate", "Advanced", "Expert"}
VALID_TREND      = {"Low", "Medium", "High"}
VALID_EMERGING   = {"Yes", "No"}
MIN_ROWS         = 100
MIN_DOMAINS      = 10


def validate(csv_path: Path | None = None) -> bool:
    csv_path = csv_path or TAXONOMY_DIR / "AcadEval_DomainTaxonomy.csv"
    errors, warnings = [], []

    # ── 1. File existence ────────────────────────────────────────────────────
    if not csv_path.exists():
        print(f"[FAIL] CSV not found: {csv_path}")
        return False
    df = pd.read_csv(csv_path, encoding="utf-8-sig")

    # ── 2. Column check ──────────────────────────────────────────────────────
    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        errors.append(f"Missing columns: {missing_cols}")

    # ── 3. Row count ─────────────────────────────────────────────────────────
    if len(df) < MIN_ROWS:
        errors.append(f"Too few rows: {len(df)} (min {MIN_ROWS})")

    # ── 4. Domain count ──────────────────────────────────────────────────────
    n_domains = df["Domain"].nunique() if "Domain" in df else 0
    if n_domains < MIN_DOMAINS:
        errors.append(f"Too few domains: {n_domains} (min {MIN_DOMAINS})")

    # ── 5. Null checks in critical columns ──────────────────────────────────
    for col in ["Taxonomy_ID", "Domain", "Sub_Domain", "Topic", "Description"]:
        if col in df and df[col].isnull().any():
            n = df[col].isnull().sum()
            errors.append(f"Null values in '{col}': {n} rows")

    # ── 6. Controlled vocabulary ─────────────────────────────────────────────
    if "Difficulty_Level" in df:
        bad = set(df["Difficulty_Level"].dropna()) - VALID_DIFFICULTY
        if bad:
            errors.append(f"Invalid Difficulty_Level values: {bad}")
    if "Trend_Level" in df:
        bad = set(df["Trend_Level"].dropna()) - VALID_TREND
        if bad:
            errors.append(f"Invalid Trend_Level values: {bad}")
    if "Emerging_Topic" in df:
        bad = set(df["Emerging_Topic"].dropna()) - VALID_EMERGING
        if bad:
            errors.append(f"Invalid Emerging_Topic values: {bad}")

    # ── 7. Duplicate Taxonomy_IDs ────────────────────────────────────────────
    if "Taxonomy_ID" in df:
        dups = df[df.duplicated("Taxonomy_ID")]["Taxonomy_ID"].tolist()
        if dups:
            errors.append(f"Duplicate Taxonomy_IDs: {dups[:5]}")

    # ── 8. Short descriptions ────────────────────────────────────────────────
    if "Description" in df:
        short = df[df["Description"].str.len() < 30]
        if not short.empty:
            warnings.append(f"{len(short)} descriptions shorter than 30 chars")

    # ── Report ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  AcadEval Taxonomy Validation Report")
    print("=" * 60)
    print(f"  File      : {csv_path.name}")
    print(f"  Rows      : {len(df)}")
    print(f"  Domains   : {n_domains}")
    print(f"  Columns   : {len(df.columns)}")
    print(f"  Errors    : {len(errors)}")
    print(f"  Warnings  : {len(warnings)}")
    print("-" * 60)

    if errors:
        print("[ERRORS]")
        for e in errors:
            print(f"  [X] {e}")
    else:
        print("  [OK] No errors found.")

    if warnings:
        print("[WARNINGS]")
        for w in warnings:
            print(f"  [!] {w}")

    # Save report
    report = {
        "status": "PASS" if not errors else "FAIL",
        "rows": len(df),
        "domains": n_domains,
        "errors": errors,
        "warnings": warnings,
    }
    (TAXONOMY_DIR / "validation_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(f"\n  Status : {'[PASS]' if not errors else '[FAIL]'}")
    print("=" * 60 + "\n")
    return not errors


if __name__ == "__main__":
    ok = validate()
    sys.exit(0 if ok else 1)
