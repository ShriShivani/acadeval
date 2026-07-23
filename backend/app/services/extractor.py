"""
Module 2 — Entity / Feature Extraction Service
================================================
Extracts structured entities (algorithms, technologies, frameworks, datasets,
hardware, applications, metrics) from free-text project proposals using
spaCy EntityRuler patterns seeded directly from AcadEval_FeatureKnowledgeBase
with an LLM verification fallback pass for unrecognized spans.
"""

import json
import logging
import re
import sys
from pathlib import Path

from app.services.llm_client import call_gemini_json

# Add feature_kb directory to sys.path
FEATURE_KB_DIR = Path(__file__).resolve().parents[3] / "datasets" / "feature_kb"
if str(FEATURE_KB_DIR) not in sys.path:
    sys.path.insert(0, str(FEATURE_KB_DIR))

try:
    from feature_kb_loader import load_feature_list, get_spacy_entity_ruler_patterns
except ImportError:
    load_feature_list = None
    get_spacy_entity_ruler_patterns = None

PENDING_REVIEW_PATH = FEATURE_KB_DIR / "pending_review.json"
KNOWN_CATEGORY_LABELS = {"algorithm", "technology", "framework", "library", "dataset", "application", "hardware", "metric"}
MAX_LLM_VERIFICATIONS_PER_CALL = 5

log = logging.getLogger(__name__)

# spaCy integration
try:
    import spacy
    from spacy.pipeline import EntityRuler
    _SPACY_AVAILABLE = True
except ImportError:
    _SPACY_AVAILABLE = False


class FeatureExtractorService:
    def __init__(self):
        self.nlp = None
        self._initialized = False

    def _lazy_init(self):
        if self._initialized:
            return

        if _SPACY_AVAILABLE:
            try:
                # Load blank or small English spacy model
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                except Exception:
                    self.nlp = spacy.blank("en")

                if get_spacy_entity_ruler_patterns:
                    patterns = get_spacy_entity_ruler_patterns()
                    ruler = self.nlp.add_pipe("entity_ruler", before="ner" if "ner" in self.nlp.pipe_names else None)
                    ruler.add_patterns(patterns)
                    log.info("Initialized spaCy EntityRuler with %d patterns for Module 2.", len(patterns))
            except Exception as e:
                log.warning("Failed to initialize spaCy EntityRuler (%s). Using regex extractor fallback.", e)
                self.nlp = None

        self._initialized = True

    def extract_entities(self, text: str) -> dict:
        """
        Extracts structured entities from text.
        Returns:
          {
            "algorithms": list[str],
            "technologies": list[str],
            "frameworks": list[str],
            "libraries": list[str],
            "datasets": list[str],
            "applications": list[str],
            "hardware": list[str],
            "unmatched_spans": list[str],
            "all_extracted": list[dict]
          }
        """
        self._lazy_init()
        extracted_by_cat = {
            "algorithms": set(),
            "technologies": set(),
            "frameworks": set(),
            "libraries": set(),
            "datasets": set(),
            "applications": set(),
            "hardware": set(),
        }
        all_extracted = []
        unmatched_candidates = []

        if self.nlp is not None:
            doc = self.nlp(text)
            for ent in doc.ents:
                label_lower = ent.label_.lower()
                cat_key = f"{label_lower}s" if not label_lower.endswith("s") else label_lower
                if label_lower == "algorithm":
                    extracted_by_cat["algorithms"].add(ent.text)
                elif label_lower == "technology":
                    extracted_by_cat["technologies"].add(ent.text)
                elif label_lower == "framework":
                    extracted_by_cat["frameworks"].add(ent.text)
                elif label_lower == "library":
                    extracted_by_cat["libraries"].add(ent.text)
                elif label_lower == "dataset":
                    extracted_by_cat["datasets"].add(ent.text)
                elif label_lower == "application":
                    extracted_by_cat["applications"].add(ent.text)
                elif label_lower == "hardware":
                    extracted_by_cat["hardware"].add(ent.text)
                elif label_lower not in KNOWN_CATEGORY_LABELS:
                    # Generic NER label (ORG, PRODUCT, GPE, ...) the EntityRuler
                    # didn't claim — candidate for LLM verification below.
                    unmatched_candidates.append(ent.text)

                all_extracted.append({
                    "text": ent.text,
                    "category": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })

        # Regex fallback / augmentation against FeatureKB list
        if load_feature_list:
            feats = load_feature_list()
            text_lower = text.lower()
            for feat in feats:
                name = feat["name"]
                cat = feat["category"].lower()
                cat_key = f"{cat}s"
                
                # Check main name and aliases
                matched = False
                if re.search(r'\b' + re.escape(name.lower()) + r'\b', text_lower):
                    matched = True
                else:
                    for alias in feat.get("aliases", []):
                        if alias and re.search(r'\b' + re.escape(alias.lower()) + r'\b', text_lower):
                            matched = True
                            break

                if matched and cat_key in extracted_by_cat:
                    extracted_by_cat[cat_key].add(name)

        # De-dup unmatched candidates and drop any that a known feature already covers
        known_names_lower = {n.lower() for cat in extracted_by_cat.values() for n in cat}
        seen = set()
        deduped_unmatched = []
        for span in unmatched_candidates:
            key = span.lower().strip()
            if key and key not in seen and key not in known_names_lower:
                seen.add(key)
                deduped_unmatched.append(span)

        still_unmatched = self._verify_unmatched_spans(deduped_unmatched, extracted_by_cat)

        return {
            "algorithms": sorted(list(extracted_by_cat["algorithms"])),
            "technologies": sorted(list(extracted_by_cat["technologies"])),
            "frameworks": sorted(list(extracted_by_cat["frameworks"])),
            "libraries": sorted(list(extracted_by_cat["libraries"])),
            "datasets": sorted(list(extracted_by_cat["datasets"])),
            "applications": sorted(list(extracted_by_cat["applications"])),
            "hardware": sorted(list(extracted_by_cat["hardware"])),
            "unmatched_spans": still_unmatched,
            "all_extracted": all_extracted
        }

    def _verify_unmatched_spans(self, spans: list[str], extracted_by_cat: dict) -> list[str]:
        """
        Module 2's "send to LLM, map-or-confirm-new" pass (Section 7.2, step 4).
        Spans Gemini maps to an existing FeatureKnowledgeBase entry get folded
        into `extracted_by_cat`; spans confirmed as genuinely new are appended
        to `pending_review.json` for manual curation and returned as still-unmatched.
        """
        if not spans or not load_feature_list:
            return spans

        known_names = [f["name"] for f in load_feature_list()]
        still_unmatched = []

        for span in spans[:MAX_LLM_VERIFICATIONS_PER_CALL]:
            prompt = f"""A project-proposal parser found the phrase "{span}" but it isn't in our known
feature vocabulary. Known feature names include: {", ".join(known_names[:150])}

Does "{span}" refer to one of these existing features (a spelling/naming variant), or is it a
genuinely new algorithm/technology/framework/library/dataset/application/hardware term?
Respond with a single JSON object only:
{{"is_new": true or false, "category": "Algorithm|Technology|Framework|Library|Dataset|Application|Hardware", "matched_name": "<existing name if not new, else null>"}}
"""
            result = call_gemini_json(prompt)
            if not result:
                still_unmatched.append(span)
                continue

            category = str(result.get("category", "")).strip().lower()
            cat_key = f"{category}s" if not category.endswith("s") else category

            if not result.get("is_new") and result.get("matched_name") and cat_key in extracted_by_cat:
                extracted_by_cat[cat_key].add(result["matched_name"])
            elif result.get("is_new"):
                self._queue_pending_review(span, category or "unknown")
                still_unmatched.append(span)
            else:
                still_unmatched.append(span)

        # Anything beyond the per-call cap is left unverified rather than dropped silently
        still_unmatched.extend(spans[MAX_LLM_VERIFICATIONS_PER_CALL:])
        return still_unmatched

    @staticmethod
    def _queue_pending_review(span: str, category: str):
        try:
            queue = []
            if PENDING_REVIEW_PATH.exists():
                queue = json.loads(PENDING_REVIEW_PATH.read_text(encoding="utf-8"))
            if not any(item["name"].lower() == span.lower() for item in queue):
                queue.append({"name": span, "category": category})
                PENDING_REVIEW_PATH.write_text(json.dumps(queue, indent=2), encoding="utf-8")
        except Exception as e:
            log.warning("Failed to queue pending-review candidate %r (%s)", span, e)


# Singleton instance
extractor_service = FeatureExtractorService()
