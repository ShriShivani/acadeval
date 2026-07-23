"""
AcadEval Domain Taxonomy Exporter
====================================
Export the taxonomy to additional formats: Markdown, HTML table,
RDF Turtle (for knowledge graph use), and a keyword index JSON.
"""

import json
import logging
from pathlib import Path

import pandas as pd

from taxonomy_loader import load_dataframe

log = logging.getLogger(__name__)
TAXONOMY_DIR = Path(__file__).parent


# ─────────────────────────────────────────────────────────────────────────────
# KEYWORD INDEX
# ─────────────────────────────────────────────────────────────────────────────

def export_keyword_index(output_dir: Path = TAXONOMY_DIR) -> Path:
    """
    Export a keyword -> [domain, sub_domain, topic] inverted index.
    Used by Module 5 (Similarity) and Module 7 (Novelty).
    """
    df = load_dataframe()
    index: dict[str, list[dict]] = {}
    kw_cols = ["Common_Keywords", "Related_Keywords", "Technologies", "Algorithms"]
    for _, row in df.iterrows():
        for col in kw_cols:
            for kw in str(row.get(col, "")).split(","):
                kw = kw.strip().lower()
                if not kw:
                    continue
                if kw not in index:
                    index[kw] = []
                index[kw].append({
                    "taxonomy_id": row["Taxonomy_ID"],
                    "domain": row["Domain"],
                    "sub_domain": row["Sub_Domain"],
                    "topic": row["Topic"],
                })
    out = output_dir / "keyword_index.json"
    out.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Keyword index → %s  (%d entries)", out, len(index))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# MARKDOWN TABLE
# ─────────────────────────────────────────────────────────────────────────────

def export_markdown(output_dir: Path = TAXONOMY_DIR) -> Path:
    """Export a concise Markdown summary grouped by domain."""
    df = load_dataframe()
    lines = [
        "# AcadEval Domain Taxonomy",
        "",
        f"**Total topics:** {len(df)} | "
        f"**Domains:** {df['Domain'].nunique()} | "
        f"**Version:** 1.0.0",
        "",
        "---",
        "",
    ]
    for domain in sorted(df["Domain"].unique()):
        lines.append(f"## {domain}")
        domain_df = df[df["Domain"] == domain]
        for sub in sorted(domain_df["Sub_Domain"].unique()):
            lines.append(f"\n### {sub}\n")
            lines.append("| ID | Topic | Difficulty | Trend | Emerging |")
            lines.append("|---|---|---|---|---|")
            sub_df = domain_df[domain_df["Sub_Domain"] == sub]
            for _, row in sub_df.iterrows():
                em = "✅" if row["Emerging_Topic"] == "Yes" else ""
                lines.append(
                    f"| {row['Taxonomy_ID']} "
                    f"| {row['Topic']} "
                    f"| {row['Difficulty_Level']} "
                    f"| {row['Trend_Level']} "
                    f"| {em} |"
                )
        lines.append("")
    out = output_dir / "AcadEval_DomainTaxonomy.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    log.info("Markdown → %s", out)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# HTML TABLE
# ─────────────────────────────────────────────────────────────────────────────

def export_html(output_dir: Path = TAXONOMY_DIR) -> Path:
    """Export an HTML version of the taxonomy with light styling."""
    df = load_dataframe()
    html_cols = [
        "Taxonomy_ID", "Domain", "Sub_Domain", "Topic",
        "Difficulty_Level", "Trend_Level", "Emerging_Topic",
        "Technologies", "Algorithms", "Typical_Datasets",
    ]
    sub_df = df[html_cols]
    html = sub_df.to_html(index=False, border=0, classes="taxonomy-table")
    styled = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AcadEval Domain Taxonomy</title>
<style>
  body {{ font-family: Inter, sans-serif; padding: 24px; }}
  h1 {{ color: #1B2A4A; }}
  .taxonomy-table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
  .taxonomy-table th {{ background: #1B2A4A; color: #fff; padding: 8px 12px; text-align: left; }}
  .taxonomy-table td {{ padding: 6px 12px; border-bottom: 1px solid #e5e7eb; }}
  .taxonomy-table tr:hover {{ background: #f0f4ff; }}
</style>
</head>
<body>
<h1>AcadEval Domain Taxonomy</h1>
<p><strong>Total:</strong> {len(df)} topics across {df['Domain'].nunique()} domains.</p>
{html}
</body>
</html>"""
    out = output_dir / "AcadEval_DomainTaxonomy.html"
    out.write_text(styled, encoding="utf-8")
    log.info("HTML → %s", out)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# RDF TURTLE (lightweight knowledge graph export)
# ─────────────────────────────────────────────────────────────────────────────

def export_rdf_turtle(output_dir: Path = TAXONOMY_DIR) -> Path:
    """Export a minimal RDF Turtle representation for knowledge graph use."""
    df = load_dataframe()
    lines = [
        "@prefix ae:   <http://acadeval.io/taxonomy#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix dc:   <http://purl.org/dc/elements/1.1/> .",
        "",
    ]
    for _, row in df.iterrows():
        tid = row["Taxonomy_ID"].replace("-", "_")
        domain_uri    = row["Domain"].replace(" ", "_").replace("/", "_")
        sub_domain_uri = row["Sub_Domain"].replace(" ", "_").replace("/", "_")
        topic_clean   = row["Topic"].replace('"', "'")
        desc_clean    = row["Description"].replace('"', "'")[:200]
        lines += [
            f"ae:{tid} a ae:Topic ;",
            f'    ae:domain ae:{domain_uri} ;',
            f'    ae:subDomain ae:{sub_domain_uri} ;',
            f'    rdfs:label "{topic_clean}" ;',
            f'    dc:description "{desc_clean}" ;',
            f'    ae:difficultyLevel "{row["Difficulty_Level"]}" ;',
            f'    ae:trendLevel "{row["Trend_Level"]}" ;',
            f'    ae:emergingTopic "{row["Emerging_Topic"]}" .',
            "",
        ]
        lines.append(f"ae:{domain_uri} rdfs:label \"{row['Domain']}\" .")
        lines.append(f"ae:{sub_domain_uri} rdfs:label \"{row['Sub_Domain']}\" .")
        lines.append("")
    out = output_dir / "AcadEval_DomainTaxonomy.ttl"
    out.write_text("\n".join(lines), encoding="utf-8")
    log.info("RDF Turtle → %s", out)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# CLI — export all formats
# ─────────────────────────────────────────────────────────────────────────────

def export_all(output_dir: Path = TAXONOMY_DIR):
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    log.info("Exporting all additional formats …")
    export_keyword_index(output_dir)
    export_markdown(output_dir)
    export_html(output_dir)
    export_rdf_turtle(output_dir)
    log.info("All exports complete.")


if __name__ == "__main__":
    export_all()
