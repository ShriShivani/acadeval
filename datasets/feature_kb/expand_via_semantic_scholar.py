import json
import logging
import requests
import time
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

KB_DIR = Path(__file__).resolve().parent
KB_PATH = KB_DIR / "AcadEval_FeatureKnowledgeBase.json"
CSV_PATH = KB_DIR / "AcadEval_FeatureKnowledgeBase.csv"

# Comprehensive list of popular machine learning and computer science datasets
TARGET_DATASETS = [
    {"name": "OpenBCI Dataset", "aliases": ["OpenBCI", "EEG OpenBCI"], "default_year": 2014, "desc": "Biosensing and EEG signal datasets gathered via OpenBCI hardware."},
    {"name": "WikiText-103", "aliases": ["WikiText103", "WikiText-2"], "default_year": 2016, "desc": "Large language modeling dataset containing over 100 million tokens extracted from Wikipedia."},
    {"name": "LibriSpeech", "aliases": ["LibriSpeech ASR corpus", "Librispeech"], "default_year": 2015, "desc": "Large-scale corpus of read English speech derived from audiobooks, used for automatic speech recognition (ASR)."},
    {"name": "CelebA", "aliases": ["CelebFaces Attributes Dataset", "CelebA Dataset"], "default_year": 2015, "desc": "Large-scale face attributes dataset with more than 200K celebrity images."},
    {"name": "Cityscapes", "aliases": ["Cityscapes Dataset"], "default_year": 2016, "desc": "Large-scale dataset for semantic urban scene understanding and pixel-level segmentation."},
    {"name": "LFW", "aliases": ["Labeled Faces in the Wild"], "default_year": 2007, "desc": "Database of face photographs designed for studying the problem of unconstrained face recognition."},
    {"name": "IMDb Movie Reviews", "aliases": ["IMDb dataset", "IMDb Reviews"], "default_year": 2011, "desc": "Binary sentiment classification dataset containing 50,000 highly polar movie reviews."},
    {"name": "AG News", "aliases": ["AG News Corpus", "AGNews"], "default_year": 2004, "desc": "Classification dataset consisting of news articles categorized into four main topics."},
    {"name": "DBpedia", "aliases": ["DBpedia Dataset", "DBpedia Ontology"], "default_year": 2007, "desc": "Structured dataset extracted from information created in various Wikimedia projects."},
    {"name": "ADE20K", "aliases": ["ADE20K Dataset", "Scene Parsing ADE20K"], "default_year": 2016, "desc": "Large-scale image dataset annotated with dense labels for scene parsing and semantic segmentation."},
    {"name": "Pascal VOC", "aliases": ["PASCAL VOC 2012", "VOC2012"], "default_year": 2005, "desc": "Standardised dataset and evaluation system for image classification, object detection, and segmentation."},
    {"name": "Yelp Reviews", "aliases": ["Yelp Academic Dataset", "Yelp Open Dataset"], "default_year": 2013, "desc": "Dataset containing millions of business reviews and merchant metadata for sentiment analysis."},
    {"name": "WordNet", "aliases": ["WordNet Database"], "default_year": 1995, "desc": "Large lexical database of English nouns, verbs, adjectives, and adverbs grouped into sets of cognitive synonyms."},
    {"name": "ESC-50", "aliases": ["ESC-50 Dataset", "Environmental Sound Classification"], "default_year": 2015, "desc": "Curated collection of 2000 environmental audio recordings categorized into 50 functional classes."},
    {"name": "FSD50K", "aliases": ["Freesound Dataset 50K"], "default_year": 2020, "desc": "Large-scale dataset of human-labeled sound events containing over 50,000 audio clips under Creative Commons licenses."},
    {"name": "UrbanSound8K", "aliases": ["UrbanSound"], "default_year": 2014, "desc": "Dataset containing 8732 labeled sound excerpts of urban noises from 10 classes."},
    {"name": "MovieLens", "aliases": ["MovieLens 100K", "MovieLens 1M", "MovieLens 20M"], "default_year": 1998, "desc": "Stable benchmark dataset for collaborative filtering and recommendation systems research."},
    {"name": "DailyDialog", "aliases": ["DailyDialog Dataset"], "default_year": 2017, "desc": "High-quality multi-turn dialog dataset covering various daily topics with emotion annotations."},
    {"name": "Cornell Movie-Dialogs", "aliases": ["Cornell Movie Dialogs Corpus"], "default_year": 2011, "desc": "Large metadata-rich collection of fictional conversations extracted from raw movie scripts."},
    {"name": "Penn Treebank", "aliases": ["PTB", "Penn Treebank Dataset"], "default_year": 1993, "desc": "Linguistic corpus containing annotated English text with part-of-speech tags and syntactic structures."},
    {"name": "Sentiment140", "aliases": ["Twitter Sentiment Dataset"], "default_year": 2009, "desc": "Dataset containing 1.6 million tweets annotated with sentiment labels for text classification."},
    {"name": "Common Voice", "aliases": ["Mozilla Common Voice"], "default_year": 2019, "desc": "Mozilla's open-source multi-language dataset of voices for training automatic speech recognition models."},
    {"name": "Waymo Open Dataset", "aliases": ["Waymo Perception Dataset"], "default_year": 2019, "desc": "High-quality multimodal sensor dataset collected by Waymo self-driving vehicles."},
    {"name": "Bot-IoT", "aliases": ["Bot-IoT Dataset"], "default_year": 2018, "desc": "IoT network traffic dataset simulated in a testbed environment with various cyber-attack categories."},
    {"name": "WMT14", "aliases": ["WMT Translation Dataset"], "default_year": 2014, "desc": "Machine translation benchmark dataset containing parallel corpora for European languages."},
    {"name": "Multi30K", "aliases": ["Multi30K Dataset"], "default_year": 2016, "desc": "Multilingual image description dataset extending Flickr30k with German, French, and Czech sentences."},
    {"name": "PubMedQA", "aliases": ["PubMedQA Dataset"], "default_year": 2019, "desc": "Biomedical question answering dataset collected from PubMed abstracts."},
    {"name": "MedQA", "aliases": ["Medical Question Answering Dataset"], "default_year": 2020, "desc": "Question answering dataset based on medical board examination questions."},
    {"name": "CheXpert", "aliases": ["CheXpert Dataset"], "default_year": 2019, "desc": "Large dataset of chest radiographs with radiologist reports, labeled for automated interpretation."},
    {"name": "CASIA-WebFace", "aliases": ["CASIA WebFace"], "default_year": 2014, "desc": "Large face dataset containing nearly 500,000 images of 10,575 subjects for face recognition research."},
    {"name": "DeepFashion", "aliases": ["DeepFashion Dataset"], "default_year": 2016, "desc": "Large-scale fashion dataset containing over 800,000 images annotated with clothing categories, attributes, and keypoints."},
    {"name": "ShapeNet", "aliases": ["ShapeNet Core"], "default_year": 2015, "desc": "Large-scale repository of 3D CAD models organized according to WordNet synsets."},
    {"name": "ModelNet40", "aliases": ["ModelNet", "Princeton ModelNet"], "default_year": 2015, "desc": "3D CAD model dataset widely used for benchmarking 3D object classification algorithms."},
    {"name": "ScanNet", "aliases": ["ScanNet v2"], "default_year": 2017, "desc": "RGB-D video dataset of indoor scenes annotated with 3D camera poses, surface reconstructions, and semantic labels."}
]

SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

def query_semantic_scholar(query: str) -> tuple[int | None, str | None]:
    """Queries Semantic Scholar API to find the earliest year and abstract/title information."""
    try:
        params = {"query": query, "limit": 5, "fields": "year,title,abstract"}
        resp = requests.get(SEMANTIC_SCHOLAR_URL, params=params, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            if not data:
                return None, None
            
            # Find earliest year in matching papers
            years = [p["year"] for p in data if p.get("year")]
            earliest_year = min(years) if years else None
            
            # Get a descriptive title/abstract snippet from the top match
            top_match = data[0]
            abstract = top_match.get("abstract")
            title = top_match.get("title")
            
            desc = abstract[:150] + "..." if abstract else title
            return earliest_year, desc
    except Exception as e:
        log.warning("Semantic Scholar query failed for %r: %s", query, e)
    return None, None

def main():
    if not KB_PATH.exists():
        log.error("Knowledge base file not found at %s", KB_PATH)
        return

    with open(KB_PATH, "r", encoding="utf-8") as f:
        existing = json.load(f)

    # Build lookup sets
    existing_names = {e["name"].lower().strip() for e in existing}
    for e in existing:
        for alias in e.get("aliases", []):
            existing_names.add(alias.lower().strip())

    added_count = 0
    next_id_num = len(existing) + 1

    log.info("Starting Semantic Scholar expansion for %d datasets...", len(TARGET_DATASETS))

    for target in TARGET_DATASETS:
        name = target["name"]
        primary_query = target["aliases"][0] if target["aliases"] else name
        
        # Check duplicates
        if name.lower().strip() in existing_names:
            log.info("Skipping existing entry: %s", name)
            continue

        log.info("Querying Semantic Scholar for: %s", name)
        fetched_year, fetched_desc = query_semantic_scholar(primary_query)
        
        # Apply defaults if Semantic Scholar query failed or returned no results
        year = fetched_year if fetched_year else target["default_year"]
        desc = fetched_desc if fetched_desc else target["desc"]
        
        # Clean description text
        desc = desc.replace("\n", " ").strip()
        if len(desc) > 200:
            desc = desc[:197] + "..."

        feature_id = f"FEAT-{next_id_num:04d}"
        new_feature = {
            "feature_id": feature_id,
            "name": name,
            "category": "Dataset",
            "aliases": target["aliases"],
            "first_seen_year": year,
            "description": desc,
            "difficulty": "Intermediate",
            "default_rarity": 0.4
        }
        
        existing.append(new_feature)
        existing_names.add(name.lower().strip())
        for alias in target["aliases"]:
            existing_names.add(alias.lower().strip())
            
        next_id_num += 1
        added_count += 1
        
        # Be nice to the API rate limits
        time.sleep(0.5)

    if added_count > 0:
        # Save updated JSON
        with open(KB_PATH, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        
        # Save updated CSV
        df = pd.DataFrame(existing)
        df_csv = df.copy()
        df_csv["aliases"] = df_csv["aliases"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        df_csv.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
        
        log.info("Success! Added %d new datasets to the Knowledge Base. Total entries: %d", added_count, len(existing))
    else:
        log.info("No new datasets were added (all already existed).")

if __name__ == "__main__":
    main()
