# AcadEval Domain Taxonomy — Dataset 2

> **Version:** 1.0.0 | **Author:** AcadEval Research Team | **License:** MIT

## Overview

`AcadEval_DomainTaxonomy` is a hierarchical academic project taxonomy covering
**44 domains**, **200+ sub-domains**, and **200+ curated topics** with rich
metadata designed for AI-powered academic project evaluation.

It serves as the knowledge base for:

| Module | Purpose |
|--------|---------|
| **Module 4** | Domain Classification |
| **Module 5** | Similarity Detection |
| **Module 7** | Novelty Analysis |

---

## Directory Structure

```
datasets/taxonomy/
├── AcadEval_DomainTaxonomy.csv      ← Primary dataset (UTF-8 BOM, Excel-safe)
├── AcadEval_DomainTaxonomy.xlsx     ← Styled Excel workbook
├── AcadEval_DomainTaxonomy.json     ← Machine-readable JSON array
├── AcadEval_DomainTaxonomy.md       ← Human-readable Markdown summary
├── AcadEval_DomainTaxonomy.html     ← Searchable HTML table
├── AcadEval_DomainTaxonomy.ttl      ← RDF Turtle (knowledge graph)
├── keyword_index.json               ← Inverted keyword → topic index
├── statistics.json                  ← Dataset statistics
├── validation_report.json           ← Validation results
├── taxonomy_generator.py            ← Generates all output files
├── taxonomy_validator.py            ← Validates the generated CSV
├── taxonomy_loader.py               ← Cached loader API
├── taxonomy_search.py               ← Keyword search + domain classification
├── taxonomy_exporter.py             ← Additional format exports
└── README.md                        ← This file
```

---

## Schema (24 Columns)

| Column | Type | Description |
|--------|------|-------------|
| `Taxonomy_ID` | str | Unique ID (`AE-0001` … `AE-NNNN`) |
| `Domain` | str | Top-level domain (44 values) |
| `Sub_Domain` | str | Sub-category within domain |
| `Topic` | str | Specific research/project topic |
| `Parent_Topic` | str | Parent concept for hierarchy |
| `Description` | str | Plain-English description |
| `Common_Keywords` | str | Comma-separated primary keywords |
| `Related_Keywords` | str | Comma-separated secondary keywords |
| `Technologies` | str | Core technologies used |
| `Algorithms` | str | Key algorithms |
| `Programming_Languages` | str | Primary languages |
| `Frameworks` | str | Frameworks and platforms |
| `Libraries` | str | Python/R/JS libraries |
| `Hardware` | str | Required hardware |
| `Typical_Datasets` | str | Well-known benchmark datasets |
| `Research_Areas` | str | Active research sub-areas |
| `Application_Areas` | str | Real-world application domains |
| `Difficulty_Level` | enum | `Beginner / Intermediate / Advanced / Expert` |
| `Industry` | str | Target industry sectors |
| `Emerging_Topic` | enum | `Yes / No` |
| `Trend_Level` | enum | `Low / Medium / High` |
| `Related_Domains` | str | Cross-domain relationships |
| `Source` | str | Data provenance |
| `Notes` | str | Additional annotations |

---

## Covered Domains (44)

| # | Domain | # | Domain |
|---|--------|---|--------|
| 1 | Artificial Intelligence | 23 | FinTech |
| 2 | Machine Learning | 24 | E-Commerce |
| 3 | Deep Learning | 25 | Embedded Systems |
| 4 | Computer Vision | 26 | Electronics |
| 5 | Natural Language Processing | 27 | Networking |
| 6 | Generative AI | 28 | Wireless Communication |
| 7 | Robotics | 29 | AR/VR |
| 8 | Internet of Things | 30 | Digital Twin |
| 9 | Cyber Security | 31 | Smart Cities |
| 10 | Blockchain | 32 | Autonomous Vehicles |
| 11 | Cloud Computing | 33 | Renewable Energy |
| 12 | Big Data | 34 | Manufacturing |
| 13 | Data Science | 35 | Industry 4.0 |
| 14 | Software Engineering | 36 | Supply Chain |
| 15 | Web Development | 37 | Business Analytics |
| 16 | Mobile Application Development | 38 | Human Computer Interaction |
| 17 | Healthcare | 39 | Computer Graphics |
| 18 | Medical Imaging | 40 | Image Processing |
| 19 | Bioinformatics | 41 | Signal Processing |
| 20 | Agriculture | 42 | Drone Technology |
| 21 | Smart Farming | 43 | GIS |
| 22 | Education | 44 | Remote Sensing |

---

## Quick Start

### Generate all dataset files

```bash
cd datasets/taxonomy
pip install pandas openpyxl
python taxonomy_generator.py
```

### Validate the dataset

```bash
python taxonomy_validator.py
```

### Export to additional formats

```bash
python taxonomy_exporter.py
```

### Use in your backend code

```python
from taxonomy_loader import classify_domain, get_keywords_for_domain

# Domain classification
result = classify_domain("Deep learning model for tumor segmentation in MRI scans")
print(result["domain"])        # → "Medical Imaging"
print(result["top_topics"])    # → ["Brain MRI Segmentation", ...]

# Get all keywords for a domain
keywords = get_keywords_for_domain("Blockchain")
```

---

## Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{acadeval_taxonomy_2026,
  title     = {AcadEval Domain Taxonomy: A Hierarchical Knowledge Base
               for AI-powered Academic Project Evaluation},
  author    = {AcadEval Research Team},
  year      = {2026},
  version   = {1.0.0},
  publisher = {AcadEval},
  url       = {https://github.com/ShriShivani/acadeval}
}
```

---

## Normalization

The taxonomy applies a canonical normalization map (defined in `taxonomy_generator.py`)
to ensure consistent technology names:

| Raw | Canonical |
|-----|-----------|
| Tensor Flow | TensorFlow |
| Py Torch | PyTorch |
| sklearn | scikit-learn |
| ReactJS | React.js |
| K8s | Kubernetes |
| GANs | GAN |

---

## Extending the Taxonomy

To add a new domain or topic:

1. Edit `taxonomy_generator.py` → add rows using the `_row(...)` helper.
2. Re-run `python taxonomy_generator.py`.
3. Re-run `python taxonomy_validator.py` to verify integrity.
4. Re-run `python taxonomy_exporter.py` for updated formats.

The schema is **frozen at 24 columns** — new rows simply extend the data,
never changing the column structure.
