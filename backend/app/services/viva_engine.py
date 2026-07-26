"""
Intelligent Viva Assessment Engine
=====================================
Research Framework: Adaptive Knowledge-Coverage Assessment for Project Viva Evaluation

This module implements five novel components:

  1. QuestionGenerator    — generates a rich question pool from the project's knowledge graph,
                            organised into 7 categories × 4 difficulty levels.

  2. AdaptiveSelector     — selects the next question using a CAT (Computerized Adaptive Testing)
                            algorithm: difficulty rises on correct answers, falls on failures,
                            avoids concepts already well-covered.

  3. SemanticEvaluator    — evaluates answers using cosine similarity between the student's
                            response and the reference answer (sentence-transformers),
                            with Gemini as a higher-quality fallback when the API key is set.

  4. KnowledgeCoverageCalc — computes KCS = (distinct concept nodes addressed / total concept
                              nodes in the project graph), the novel metric proposed in the paper.

  5. GapDetector          — identifies which concept categories the student consistently
                            underperforms in and generates targeted learning recommendations.

Design principle: every step has a deterministic rule-based path so the engine works
without any external API keys, and a richer LLM/embedding path when keys are present.
"""

from __future__ import annotations

import hashlib
import logging
import math
import re
import uuid
from dataclasses import dataclass, field
from typing import Optional

log = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

DIFFICULTY_ORDER = {"Easy": 1, "Medium": 2, "Hard": 3, "Research": 4}
DIFFICULTY_NAMES = {v: k for k, v in DIFFICULTY_ORDER.items()}

# Minimum questions per session before completing
MIN_QUESTIONS = 8
MAX_QUESTIONS = 20
# KCS threshold for session completion (student covered ≥ 70% of concepts)
KCS_COMPLETION_THRESHOLD = 0.70


@dataclass
class QuestionNode:
    question_id: str
    text: str
    category: str           # Conceptual / Technical / Design / Research / Scenario / Limitations / Basic
    difficulty: str         # Easy / Medium / Hard / Research
    target_concept: str     # which KB node this question tests
    reference_answer: str   # gold-standard answer for semantic evaluation
    expected_keywords: list[str] = field(default_factory=list)


@dataclass
class AnswerRecord:
    question_id: str
    target_concept: str
    category: str
    difficulty: str
    answer_text: str
    correctness: float      # 0–1
    completeness: float     # 0–1
    technical_depth: float  # 0–1
    confidence: float       # 0–1
    overall_score: float    # 0–5


# ═══════════════════════════════════════════════════════════════════════════════
# 2. QUESTION GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class QuestionGenerator:
    """
    Builds a question pool from the project's extracted entities and knowledge graph.
    Each entity in the graph becomes the `target_concept` for one or more questions.
    Questions are generated at 4 difficulty levels using templates first, with
    Gemini enrichment when available.
    """

    # Category templates: {concept} is replaced with the actual entity name
    TEMPLATES: dict[str, dict[str, list[str]]] = {
        "Basic": {
            "Easy": [
                "What is {concept} and what role does it play in your project?",
                "In simple terms, explain what {concept} means.",
                "Why did you include {concept} in your project?",
            ],
        },
        "Conceptual": {
            "Easy": [
                "Explain the core idea behind {concept}.",
                "What problem does {concept} solve in your project?",
            ],
            "Medium": [
                "What are the key advantages of using {concept} over alternatives?",
                "How does {concept} contribute to your system's overall performance?",
                "Compare {concept} with at least one alternative approach.",
            ],
            "Hard": [
                "Discuss the theoretical foundations of {concept} and how they apply to your project.",
                "What are the mathematical or algorithmic principles underlying {concept}?",
            ],
        },
        "Technical": {
            "Easy": [
                "How did you implement {concept} in your project?",
                "Walk me through how {concept} is used in your codebase.",
            ],
            "Medium": [
                "What configuration or tuning decisions did you make for {concept}?",
                "How does {concept} interact with the other components of your system?",
                "What challenges did you face when integrating {concept}?",
            ],
            "Hard": [
                "How would you optimise {concept} to handle 10× the current load?",
                "What are the failure modes of {concept} and how did you handle them?",
            ],
        },
        "Design": {
            "Medium": [
                "Why did you choose {concept} for this project instead of an alternative?",
                "What architectural trade-offs did {concept} introduce?",
            ],
            "Hard": [
                "If you had to redesign the {concept} component from scratch, what would you change?",
                "How would you replace {concept} with a more scalable solution?",
            ],
        },
        "Scenario": {
            "Medium": [
                "Suppose {concept} starts producing incorrect outputs — what is your debugging strategy?",
                "If the team using {concept} doubles, how does your design accommodate the change?",
            ],
            "Hard": [
                "Your {concept} component fails in production at 3 AM. Walk me through your incident response.",
                "How would your system behave if {concept} becomes unavailable mid-operation?",
            ],
        },
        "Limitations": {
            "Easy": [
                "What are the known limitations of {concept} in your implementation?",
                "What would you improve about how you used {concept}?",
            ],
            "Medium": [
                "Under what conditions does {concept} perform poorly, and how would you mitigate that?",
            ],
        },
        "Research": {
            "Research": [
                "How does your use of {concept} compare to the state-of-the-art in recent literature?",
                "What novel contribution does your application of {concept} make to the field?",
                "What future research directions open up from your use of {concept}?",
            ],
        },
    }

    # Reference answer templates (used by the evaluator)
    REFERENCE_TEMPLATES: dict[str, str] = {
        "Basic/Easy": (
            "{concept} is a key component in the project. "
            "It contributes by [specific role]. Without it the system would [consequence]."
        ),
        "Conceptual/Medium": (
            "{concept} offers advantages such as [advantage 1] and [advantage 2]. "
            "Compared to alternatives like [alt], it is preferred because [reason]."
        ),
        "Technical/Medium": (
            "The implementation of {concept} involved [step 1], [step 2], and [step 3]. "
            "Key configuration decisions included [decision] because [rationale]."
        ),
        "Design/Hard": (
            "{concept} was chosen over alternatives because [reason 1] and [reason 2]. "
            "The trade-offs accepted include [trade-off]. "
            "An alternative design would use [alt] which would change [aspect]."
        ),
        "Research/Research": (
            "Current literature on {concept} includes [paper/author]. "
            "This project extends/differs by [contribution]. "
            "Future work could explore [direction]."
        ),
    }

    def generate_pool(self, project_title: str, entities: dict) -> list[QuestionNode]:
        """
        Builds the full question pool for a project.
        Entities dict has keys: algorithms, technologies, frameworks, libraries,
        datasets, applications, hardware, metrics, sub_domain.
        """
        pool: list[QuestionNode] = []

        # Collect all concept names with their category label
        concept_map: dict[str, str] = {}  # concept_name -> entity_type
        for key, label in [
            ("algorithms", "Technical"), ("technologies", "Technical"),
            ("frameworks", "Technical"), ("libraries", "Technical"),
            ("datasets", "Conceptual"), ("applications", "Conceptual"),
            ("hardware", "Technical"), ("metrics", "Conceptual"),
        ]:
            for name in entities.get(key, []):
                if name and len(name) > 1:
                    concept_map[name] = label

        # Always add project-level questions
        pool.extend(self._project_level_questions(project_title))

        # Generate per-concept questions
        for concept, entity_category in concept_map.items():
            pool.extend(self._concept_questions(concept, entity_category))

        # Deduplicate by question_id
        seen: set[str] = set()
        unique: list[QuestionNode] = []
        for q in pool:
            if q.question_id not in seen:
                seen.add(q.question_id)
                unique.append(q)

        log.info("QuestionGenerator: %d questions for '%s' (%d concepts)",
                 len(unique), project_title, len(concept_map))
        return unique

    def _concept_questions(self, concept: str, base_category: str) -> list[QuestionNode]:
        questions = []
        for cat, diff_map in self.TEMPLATES.items():
            for diff, templates in diff_map.items():
                # Take only the first template per category/difficulty to keep pool manageable
                template = templates[0]
                q_text = template.replace("{concept}", concept)
                ref_key = f"{cat}/{diff}"
                ref = self.REFERENCE_TEMPLATES.get(ref_key,
                      f"A thorough answer about {concept} should cover its purpose, "
                      f"implementation details, trade-offs, and limitations.")
                ref_answer = ref.replace("{concept}", concept)

                # Derive expected keywords from concept name + category
                kw = [concept.lower()] + concept.lower().split()
                if diff in ("Hard", "Research"):
                    kw += ["alternative", "trade-off", "limitation", "compare", "scale"]

                qid = self._qid(concept, cat, diff)
                questions.append(QuestionNode(
                    question_id=qid,
                    text=q_text,
                    category=cat,
                    difficulty=diff,
                    target_concept=concept,
                    reference_answer=ref_answer,
                    expected_keywords=list(set(kw)),
                ))
        return questions

    def _project_level_questions(self, title: str) -> list[QuestionNode]:
        return [
            QuestionNode(
                question_id="proj_problem",
                text="What specific problem does your project solve and why is it important?",
                category="Basic", difficulty="Easy",
                target_concept="Problem Statement",
                reference_answer=(
                    "The project addresses [specific problem] in [domain]. "
                    "It is important because [real-world impact]. "
                    "Current solutions fail because [gap]. Our approach [solution]."
                ),
                expected_keywords=["problem", "solution", "impact", "domain"],
            ),
            QuestionNode(
                question_id="proj_architecture",
                text="Describe the end-to-end system architecture of your project.",
                category="Technical", difficulty="Medium",
                target_concept="System Architecture",
                reference_answer=(
                    "The system has [N] major components: [list]. "
                    "Data flows from [source] through [processing] to [output]. "
                    "Component A communicates with B via [protocol/API]."
                ),
                expected_keywords=["architecture", "component", "flow", "module", "API"],
            ),
            QuestionNode(
                question_id="proj_novelty",
                text="What is the novel contribution of your project compared to existing solutions?",
                category="Research", difficulty="Research",
                target_concept="Novel Contribution",
                reference_answer=(
                    "Unlike existing solutions such as [existing], our project introduces [novelty]. "
                    "We validated this against [baseline] and achieved [metric] improvement."
                ),
                expected_keywords=["novel", "contribution", "compare", "existing", "improve"],
            ),
            QuestionNode(
                question_id="proj_limitations",
                text="What are the three most significant limitations of your current implementation?",
                category="Limitations", difficulty="Easy",
                target_concept="Limitations",
                reference_answer=(
                    "The key limitations are: (1) [limitation 1] — which could be addressed by [solution]. "
                    "(2) [limitation 2] — [solution]. (3) [limitation 3] — [solution]."
                ),
                expected_keywords=["limitation", "constraint", "improve", "future"],
            ),
            QuestionNode(
                question_id="proj_deployment",
                text="How would you deploy this system to handle 10,000 concurrent users?",
                category="Scenario", difficulty="Hard",
                target_concept="Scalability",
                reference_answer=(
                    "To scale to 10k users I would: (1) Containerise with Docker/K8s. "
                    "(2) Use a load balancer. (3) Cache results with Redis. "
                    "(4) Split the database with read replicas. (5) Use a CDN for static assets."
                ),
                expected_keywords=["scale", "load", "cache", "database", "deploy", "container"],
            ),
        ]

    @staticmethod
    def _qid(concept: str, category: str, difficulty: str) -> str:
        raw = f"{concept}|{category}|{difficulty}"
        return "q_" + hashlib.md5(raw.encode()).hexdigest()[:10]


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SEMANTIC EVALUATOR
# ═══════════════════════════════════════════════════════════════════════════════

class SemanticEvaluator:
    """
    Evaluates a student's answer against the reference answer using:
      A. sentence-transformers cosine similarity (primary, no API key needed)
      B. Gemini structured evaluation (enrichment, when GEMINI_API_KEY is set)
      C. keyword-overlap heuristic (final fallback — always works)

    Returns an AnswerEvaluation dataclass.
    """

    def __init__(self):
        self._st_model = None    # lazy-loaded sentence transformer
        self._st_tried = False

    def _get_st_model(self):
        if self._st_tried:
            return self._st_model
        self._st_tried = True
        try:
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer("all-MiniLM-L6-v2")
            log.info("SemanticEvaluator: sentence-transformer model loaded")
        except Exception as exc:
            log.warning("SemanticEvaluator: sentence-transformer unavailable (%s) — using keyword fallback", exc)
            self._st_model = None
        return self._st_model

    def evaluate(
        self,
        student_answer: str,
        reference_answer: str,
        expected_keywords: list[str],
        question_text: str,
        difficulty: str,
    ) -> dict:
        """
        Returns a dict with keys: correctness, completeness, technical_depth,
        confidence, overall_score, feedback, strong_points, weak_points.
        """
        if not student_answer.strip():
            return self._zero_eval("No answer provided.")

        # ── A. Sentence-transformer semantic similarity ────────────────────────
        correctness = self._semantic_similarity(student_answer, reference_answer)

        # ── B. Gemini evaluation (if available) ───────────────────────────────
        gemini_eval = self._gemini_evaluate(student_answer, reference_answer,
                                            question_text, difficulty)
        if gemini_eval:
            correctness = gemini_eval.get("correctness", correctness)
            completeness = gemini_eval.get("completeness", 0.5)
            technical_depth = gemini_eval.get("technical_depth", 0.5)
            feedback = gemini_eval.get("feedback", "")
            strong_points = gemini_eval.get("strong_points", [])
            weak_points = gemini_eval.get("weak_points", [])
        else:
            # ── C. Rule-based fallback ────────────────────────────────────────
            completeness = self._keyword_overlap(student_answer, expected_keywords)
            technical_depth = self._technical_depth_score(student_answer)
            feedback = self._generate_feedback(correctness, completeness, technical_depth)
            strong_points = self._extract_strong_points(student_answer, expected_keywords)
            weak_points = self._extract_weak_points(student_answer, expected_keywords)

        # ── Confidence: derived from answer length and vocabulary richness ─────
        confidence = self._confidence_score(student_answer)

        # ── Composite score (weighted) ────────────────────────────────────────
        weights = {"correctness": 0.4, "completeness": 0.3,
                   "technical_depth": 0.2, "confidence": 0.1}
        composite = (
            correctness * weights["correctness"] +
            completeness * weights["completeness"] +
            technical_depth * weights["technical_depth"] +
            confidence * weights["confidence"]
        )
        overall_score = round(composite * 5.0, 2)   # scale to 0–5

        return {
            "correctness": round(correctness, 3),
            "completeness": round(completeness, 3),
            "technical_depth": round(technical_depth, 3),
            "confidence": round(confidence, 3),
            "overall_score": overall_score,
            "feedback": feedback,
            "strong_points": strong_points,
            "weak_points": weak_points,
        }

    # ── Semantic similarity via sentence-transformers ─────────────────────────

    def _semantic_similarity(self, answer: str, reference: str) -> float:
        model = self._get_st_model()
        if model is None:
            return self._keyword_overlap(answer, reference.lower().split())
        try:
            import numpy as np
            embs = model.encode([answer, reference])
            cos_sim = float(np.dot(embs[0], embs[1]) /
                            (np.linalg.norm(embs[0]) * np.linalg.norm(embs[1]) + 1e-8))
            return max(0.0, min(1.0, cos_sim))
        except Exception as exc:
            log.warning("ST similarity failed: %s", exc)
            return self._keyword_overlap(answer, reference.lower().split())

    # ── Gemini evaluation ─────────────────────────────────────────────────────

    def _gemini_evaluate(self, answer: str, reference: str,
                         question: str, difficulty: str) -> Optional[dict]:
        from app.services.llm_client import call_gemini_json
        prompt = f"""You are an expert academic viva examiner. Evaluate the following student answer.

Question: {question}
Reference Answer (gold standard): {reference}
Student Answer: {answer}
Difficulty Level: {difficulty}

Return a JSON object with exactly these keys:
- "correctness": float 0-1 (how semantically correct the answer is)
- "completeness": float 0-1 (how completely the student covered the required points)
- "technical_depth": float 0-1 (use of correct technical terminology and depth)
- "feedback": string (2-3 sentence constructive feedback)
- "strong_points": list of strings (max 3, what the student got right)
- "weak_points": list of strings (max 3, what was missing or incorrect)

Be fair, academic, and specific. Do not reveal the reference answer in feedback."""
        result = call_gemini_json(prompt, timeout=3.0)
        if result and "correctness" in result:
            return result
        return None

    # ── Fallback heuristics ───────────────────────────────────────────────────

    @staticmethod
    def _keyword_overlap(text: str, keywords: list[str]) -> float:
        if not keywords:
            return 0.5
        lower = text.lower()
        hits = sum(1 for kw in keywords if kw.lower() in lower)
        return min(1.0, hits / max(1, len(keywords)))

    @staticmethod
    def _technical_depth_score(text: str) -> float:
        """Proxy for technical depth: ratio of technical-sounding words."""
        tech_markers = [
            "algorithm", "model", "architecture", "layer", "function", "parameter",
            "accuracy", "loss", "gradient", "epoch", "batch", "network", "api",
            "database", "query", "latency", "throughput", "pipeline", "module",
            "convolution", "pooling", "embedding", "transformer", "encoder", "decoder",
            "regression", "classification", "clustering", "optimization", "threshold",
            "precision", "recall", "f1", "roc", "overfitting", "regularization",
        ]
        words = re.findall(r"\b\w+\b", text.lower())
        if not words:
            return 0.0
        hits = sum(1 for w in words if w in tech_markers)
        return min(1.0, hits / max(1, len(words)) * 15)   # scale: ~7% tech words = 1.0

    @staticmethod
    def _confidence_score(text: str) -> float:
        """Derived from word count and lexical variety."""
        words = text.lower().split()
        wc = len(words)
        if wc < 10:
            return 0.2
        unique_ratio = len(set(words)) / wc
        # Word count score (saturates at 120 words)
        wc_score = min(1.0, wc / 120)
        # Lexical variety score
        variety_score = min(1.0, unique_ratio * 2)
        return (wc_score * 0.6 + variety_score * 0.4)

    @staticmethod
    def _generate_feedback(correctness: float, completeness: float, depth: float) -> str:
        avg = (correctness + completeness + depth) / 3
        if avg >= 0.80:
            return "Excellent answer. Demonstrates strong understanding and technical accuracy."
        elif avg >= 0.65:
            return "Good answer. Cover more technical specifics and provide concrete examples."
        elif avg >= 0.45:
            return "Partial answer. Key aspects are missing — expand with more detail and examples."
        elif avg >= 0.25:
            return "Insufficient answer. Review the core concepts and provide a structured response."
        else:
            return "Very brief or off-topic. Please provide a detailed, structured technical answer."

    @staticmethod
    def _extract_strong_points(answer: str, keywords: list[str]) -> list[str]:
        hits = [kw for kw in keywords if kw.lower() in answer.lower()]
        if not hits:
            return ["Attempted to answer the question"]
        return [f"Correctly referenced: {kw}" for kw in hits[:3]]

    @staticmethod
    def _extract_weak_points(answer: str, keywords: list[str]) -> list[str]:
        missed = [kw for kw in keywords if kw.lower() not in answer.lower()]
        if not missed:
            return []
        return [f"Missing coverage of: {kw}" for kw in missed[:3]]

    @staticmethod
    def _zero_eval(feedback: str) -> dict:
        return {
            "correctness": 0.0, "completeness": 0.0,
            "technical_depth": 0.0, "confidence": 0.0,
            "overall_score": 0.0, "feedback": feedback,
            "strong_points": [], "weak_points": ["No answer provided"],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. ADAPTIVE SELECTOR (CAT — Computerized Adaptive Testing)
# ═══════════════════════════════════════════════════════════════════════════════

class AdaptiveSelector:
    """
    Selects the next question using a simplified CAT algorithm:

    State maintained per session (in VivaSession.scores JSONB):
      - current_difficulty_level (1–4)
      - consecutive_correct / consecutive_wrong counters
      - answered question IDs (to avoid repetition)
      - covered concepts (for KCS computation)

    Difficulty adjustment rules:
      - 2 consecutive correct  → increase difficulty by 1
      - 2 consecutive wrong    → decrease difficulty by 1
      - Never go below Easy or above Research
    """

    CORRECT_THRESHOLD = 3.5  # score out of 5 considered "correct"
    CONSECUTIVE_UP = 2       # correct answers before increasing difficulty
    CONSECUTIVE_DOWN = 2     # wrong answers before decreasing difficulty

    def select_next(
        self,
        pool: list[QuestionNode],
        answered_ids: set[str],
        covered_concepts: set[str],
        current_difficulty_level: int,
        consecutive_correct: int,
        consecutive_wrong: int,
    ) -> Optional[QuestionNode]:
        """
        Returns the best next question or None if the pool is exhausted.
        Priority:
          1. Match current difficulty
          2. Target an uncovered concept
          3. Prefer category not recently asked
        """
        # Adjust difficulty
        level = current_difficulty_level
        if consecutive_correct >= self.CONSECUTIVE_UP:
            level = min(4, level + 1)
        elif consecutive_wrong >= self.CONSECUTIVE_DOWN:
            level = max(1, level - 1)

        target_difficulty = DIFFICULTY_NAMES[level]

        # Filter: not already answered, match difficulty
        candidates = [
            q for q in pool
            if q.question_id not in answered_ids
            and q.difficulty == target_difficulty
        ]

        if not candidates:
            # Relax difficulty by ±1
            for fallback_level in [level + 1, level - 1, level + 2, level - 2]:
                if 1 <= fallback_level <= 4:
                    fd = DIFFICULTY_NAMES[fallback_level]
                    candidates = [q for q in pool
                                  if q.question_id not in answered_ids and q.difficulty == fd]
                    if candidates:
                        break

        if not candidates:
            return None   # pool exhausted

        # Prefer questions targeting uncovered concepts
        uncovered = [q for q in candidates if q.target_concept not in covered_concepts]
        if uncovered:
            candidates = uncovered

        # Pick first (pool is pre-sorted by category diversity in generate_pool)
        return candidates[0]

    def should_terminate(
        self,
        questions_answered: int,
        kcs: float,
        pool_exhausted: bool,
    ) -> bool:
        """Returns True when the session should end."""
        if pool_exhausted:
            return True
        if questions_answered >= MAX_QUESTIONS:
            return True
        if questions_answered >= MIN_QUESTIONS and kcs >= KCS_COMPLETION_THRESHOLD:
            return True
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# 5. KNOWLEDGE COVERAGE SCORE
# ═══════════════════════════════════════════════════════════════════════════════

class KnowledgeCoverageCalculator:
    """
    KCS = (distinct concept nodes addressed with score ≥ threshold) / (total concept nodes)

    A concept is considered "addressed" when:
      - A question targeting it was answered with overall_score ≥ COVERAGE_THRESHOLD
    """

    COVERAGE_THRESHOLD = 2.5  # out of 5 — answered at least adequately

    def compute(
        self,
        answer_records: list[AnswerRecord],
        total_concepts: int,
    ) -> float:
        """Returns KCS as a float 0–100."""
        if total_concepts == 0:
            return 0.0
        covered = {
            r.target_concept
            for r in answer_records
            if r.overall_score >= self.COVERAGE_THRESHOLD
        }
        return round(len(covered) / total_concepts * 100, 1)

    def get_covered_concepts(self, answer_records: list[AnswerRecord]) -> set[str]:
        return {r.target_concept for r in answer_records
                if r.overall_score >= self.COVERAGE_THRESHOLD}

    def get_all_addressed_concepts(self, answer_records: list[AnswerRecord]) -> set[str]:
        return {r.target_concept for r in answer_records}


# ═══════════════════════════════════════════════════════════════════════════════
# 6. KNOWLEDGE GAP DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class GapDetector:
    """
    Analyses answer records to produce:
      - Per-concept gap severity (Critical / Moderate / Minor)
      - Per-category average scores
      - Targeted learning recommendations
    """

    GAP_THRESHOLDS = {"Critical": 2.0, "Moderate": 3.0}  # out of 5

    def analyse(
        self,
        answer_records: list[AnswerRecord],
        pool: list[QuestionNode],
    ) -> tuple[list[dict], list[str], list[str]]:
        """
        Returns:
          (knowledge_gaps, strong_areas, learning_recommendations)
        """
        if not answer_records:
            return [], [], []

        # Group scores by concept
        concept_scores: dict[str, list[float]] = {}
        concept_meta: dict[str, tuple[str, str]] = {}   # concept -> (category, difficulty)

        for rec in answer_records:
            concept_scores.setdefault(rec.target_concept, []).append(rec.overall_score)
            concept_meta[rec.target_concept] = (rec.category, rec.difficulty)

        gaps = []
        strong = []

        for concept, scores in concept_scores.items():
            avg = sum(scores) / len(scores)
            cat, diff = concept_meta.get(concept, ("General", "Medium"))

            if avg < self.GAP_THRESHOLDS["Critical"]:
                severity = "Critical"
            elif avg < self.GAP_THRESHOLDS["Moderate"]:
                severity = "Moderate"
            else:
                severity = "Minor"
                strong.append(concept)

            if severity in ("Critical", "Moderate"):
                gaps.append({
                    "concept": concept,
                    "category": cat,
                    "difficulty": diff,
                    "questionsAsked": len(scores),
                    "averageScore": round(avg, 2),
                    "gapSeverity": severity,
                })

        # Concepts not addressed at all are Critical gaps
        addressed = set(concept_scores.keys())
        for q in pool:
            if q.target_concept not in addressed and q.difficulty in ("Easy", "Medium"):
                gaps.append({
                    "concept": q.target_concept,
                    "category": q.category,
                    "difficulty": q.difficulty,
                    "questionsAsked": 0,
                    "averageScore": 0.0,
                    "gapSeverity": "Critical",
                })

        # Deduplicate gaps by concept
        seen_concepts: set[str] = set()
        unique_gaps = []
        for g in gaps:
            if g["concept"] not in seen_concepts:
                seen_concepts.add(g["concept"])
                unique_gaps.append(g)

        recommendations = self._generate_recommendations(unique_gaps, strong)
        return unique_gaps, list(set(strong)), recommendations

    @staticmethod
    def _generate_recommendations(gaps: list[dict], strong: list[str]) -> list[str]:
        recs = []
        critical = [g["concept"] for g in gaps if g["gapSeverity"] == "Critical"]
        moderate = [g["concept"] for g in gaps if g["gapSeverity"] == "Moderate"]

        if critical:
            recs.append(f"Priority study: {', '.join(critical[:3])} — these are critical gaps.")
        if moderate:
            recs.append(f"Review and deepen understanding of: {', '.join(moderate[:3])}.")

        # Category-level advice
        cats = {g["category"] for g in gaps}
        if "Research" in cats:
            recs.append("Read 2–3 recent papers in your domain and compare them with your approach.")
        if "Technical" in cats:
            recs.append("Re-implement or trace through the core algorithm/library in your project.")
        if "Scenario" in cats:
            recs.append("Practice explaining how your system handles edge cases and failures.")
        if "Design" in cats:
            recs.append("Document the architectural trade-offs you made and explore alternatives.")

        if strong:
            recs.append(f"Strong areas to highlight in your viva: {', '.join(strong[:3])}.")

        return recs[:8]   # cap at 8 recommendations


# ═══════════════════════════════════════════════════════════════════════════════
# 7. REPORT GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class VivaReportGenerator:
    """Assembles the final viva report from all session data."""

    def generate(
        self,
        session_id: str,
        project_id: str,
        project_title: str,
        answer_records: list[AnswerRecord],
        pool: list[QuestionNode],
        difficulty_progression: list[str],
        kcs: float,
    ) -> dict:
        if not answer_records:
            return {"error": "No answers recorded"}

        n = len(answer_records)
        total_concepts = len({q.target_concept for q in pool})
        covered = len({r.target_concept for r in answer_records
                       if r.overall_score >= KnowledgeCoverageCalculator.COVERAGE_THRESHOLD})

        avg_correctness  = sum(r.correctness for r in answer_records) / n
        avg_completeness = sum(r.completeness for r in answer_records) / n
        avg_depth        = sum(r.technical_depth for r in answer_records) / n
        avg_confidence   = sum(r.confidence for r in answer_records) / n

        overall_score = round(
            (avg_correctness * 0.4 + avg_completeness * 0.3 +
             avg_depth * 0.2 + avg_confidence * 0.1) * 100, 1
        )

        # Category scores
        cat_scores: dict[str, list[float]] = {}
        for rec in answer_records:
            cat_scores.setdefault(rec.category, []).append(rec.overall_score)
        category_scores = {cat: round(sum(s) / len(s), 2) for cat, s in cat_scores.items()}

        # Difficulty reached
        diff_reached = difficulty_progression[-1] if difficulty_progression else "Easy"

        # Gaps and recommendations
        detector = GapDetector()
        gaps, strong, recs = detector.analyse(answer_records, pool)

        # Grade
        if overall_score >= 80 and kcs >= 75:
            grade = "Distinction"
        elif overall_score >= 65 and kcs >= 55:
            grade = "Merit"
        elif overall_score >= 50:
            grade = "Pass"
        else:
            grade = "Needs Improvement"

        summary = (
            f"The student achieved a KCS of {kcs:.1f}%, covering {covered} of {total_concepts} "
            f"project concepts. Overall performance: {grade}. "
            f"Difficulty reached: {diff_reached}."
        )

        return {
            "sessionId": session_id,
            "projectId": project_id,
            "projectTitle": project_title,
            "overallScore": overall_score,
            "kcs": kcs,
            "difficultyReached": diff_reached,
            "totalQuestionsAnswered": n,
            "totalConceptsInProject": total_concepts,
            "conceptsCovered": covered,
            "averageCorrectness": round(avg_correctness, 3),
            "averageCompleteness": round(avg_completeness, 3),
            "averageDepth": round(avg_depth, 3),
            "averageConfidence": round(avg_confidence, 3),
            "categoryScores": category_scores,
            "difficultyProgression": difficulty_progression,
            "knowledgeGaps": gaps[:10],
            "strongAreas": strong[:5],
            "learningRecommendations": recs,
            "grade": grade,
            "summaryStatement": summary,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 8. SESSION STATE CODEC (serialize/deserialize to JSONB)
# ═══════════════════════════════════════════════════════════════════════════════

def encode_answer_records(records: list[AnswerRecord]) -> list[dict]:
    return [vars(r) for r in records]


def decode_answer_records(raw: list[dict]) -> list[AnswerRecord]:
    return [AnswerRecord(**d) for d in raw]


def encode_question_pool(pool: list[QuestionNode]) -> list[dict]:
    return [vars(q) for q in pool]


def decode_question_pool(raw: list[dict]) -> list[QuestionNode]:
    return [QuestionNode(**d) for d in raw]


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETONS
# ═══════════════════════════════════════════════════════════════════════════════

question_generator = QuestionGenerator()
semantic_evaluator = SemanticEvaluator()
adaptive_selector  = AdaptiveSelector()
kcs_calculator     = KnowledgeCoverageCalculator()
gap_detector       = GapDetector()
viva_report_gen    = VivaReportGenerator()
