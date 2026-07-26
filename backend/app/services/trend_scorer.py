"""
Module 8 — Research Trend Scoring Service
==========================================
Computes research trend signals (growth rate, paper counts, citation velocity)
by querying the Semantic Scholar Graph API and persisting yearly stats into
the `acadeval_trendbase` PostgreSQL table.

Formula:
  trend_score = (papers_last_year - papers_3_years_ago) / max(papers_3_years_ago, 1)
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.trend import TrendBaseRecord
from app.services.semantic_scholar import ss_client

log = logging.getLogger(__name__)

DEFAULT_TOPICS = [
    "deep learning", "machine learning", "computer vision", "natural language processing",
    "reinforcement learning", "federated learning", "graph neural network",
    "transformer attention", "large language model", "object detection",
    "semantic segmentation", "anomaly detection", "time series forecasting",
    "robotics autonomous systems", "edge computing IoT", "blockchain security",
    "bioinformatics genomics", "medical image analysis", "drug discovery AI",
    "quantum computing", "augmented reality", "speech recognition",
    "recommendation system", "knowledge graph", "explainable AI",
]


class TrendScorerService:
    def get_topic_trend(self, topic_query: str, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Computes trend scores for a topic using Semantic Scholar API data,
        persisting yearly paper & citation counts to PostgreSQL (`acadeval_trendbase`).
        
        Calculation:
          trend_score = (papers_last_year - papers_3_years_ago) / max(papers_3_years_ago, 1)
        """
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True

        try:
            # 1. Fetch search data from Semantic Scholar API via ss_client
            ss_data = ss_client.get_topic_trend(topic_query)
            
            if ss_data.get("data_source") == "fallback":
                # Check DB cache for historical trend data if API is unavailable
                db_records = db.query(TrendBaseRecord).filter(
                    TrendBaseRecord.topic == topic_query.lower().strip()
                ).order_by(TrendBaseRecord.year.desc()).all()

                if db_records:
                    return self._compute_trend_from_records(topic_query, db_records, source="pg_trendbase")

                return {
                    "topic": topic_query,
                    "trend_score": 0.0,
                    "growth_rate_pct": None,
                    "paper_count_3yr": None,
                    "citation_velocity": None,
                    "trend_status": "unavailable",
                    "top_papers": [],
                    "data_source": "fallback",
                }

            # 2. Extract yearly counts from Semantic Scholar search results
            papers = ss_client.search_papers(topic_query, limit=50)
            
            current_year = datetime.now(timezone.utc).year
            last_year = current_year - 1
            three_years_ago = current_year - 3

            yearly_counts: Dict[int, int] = {}
            yearly_citations: Dict[int, int] = {}

            for p in papers:
                y = p.get("year")
                if y:
                    yearly_counts[y] = yearly_counts.get(y, 0) + 1
                    yearly_citations[y] = yearly_citations.get(y, 0) + p.get("citationCount", 0)

            # 3. Persist / Update yearly counts in PostgreSQL (acadeval_trendbase)
            topic_key = topic_query.lower().strip()
            for y, count in yearly_counts.items():
                rec = db.query(TrendBaseRecord).filter(
                    TrendBaseRecord.topic == topic_key,
                    TrendBaseRecord.year == y
                ).first()

                if rec:
                    rec.paper_count = count
                    rec.citation_count = yearly_citations.get(y, 0)
                    rec.updated_at = datetime.now(timezone.utc)
                else:
                    rec = TrendBaseRecord(
                        topic=topic_key,
                        year=y,
                        paper_count=count,
                        citation_count=yearly_citations.get(y, 0)
                    )
                    db.add(rec)
            db.commit()

            # 4. Compute formula: trend_score = (papers_last_year - papers_3_years_ago) / max(papers_3_years_ago, 1)
            papers_last_year = yearly_counts.get(last_year, len([p for p in papers if p.get("year") == last_year]))
            papers_3_years_ago = yearly_counts.get(three_years_ago, len([p for p in papers if p.get("year") == three_years_ago]))

            denom = max(papers_3_years_ago, 1)
            trend_score = round((papers_last_year - papers_3_years_ago) / float(denom), 3)

            growth_rate_pct = ss_data.get("growth_rate_pct", round(trend_score * 100.0, 1))
            trend_status = "Emerging" if trend_score > 0.3 else ("Hot" if trend_score > 0.15 else "Steady")

            return {
                "topic": topic_query,
                "trend_score": trend_score,
                "growth_rate_pct": growth_rate_pct,
                "paper_count_3yr": ss_data.get("paper_count_3yr", len(papers)),
                "citation_velocity": ss_data.get("citation_velocity", 0.0),
                "trend_status": trend_status,
                "top_papers": ss_data.get("top_papers", []),
                "data_source": ss_data.get("data_source", "semantic_scholar"),
                "papers_last_year": papers_last_year,
                "papers_3_years_ago": papers_3_years_ago,
            }

        except Exception as exc:
            db.rollback()
            log.warning("TrendScorerService error for %r: %s", topic_query, exc)
            return {
                "topic": topic_query,
                "trend_score": 0.0,
                "growth_rate_pct": None,
                "paper_count_3yr": None,
                "citation_velocity": None,
                "trend_status": "unavailable",
                "top_papers": [],
                "data_source": "fallback",
            }
        finally:
            if should_close_db:
                db.close()

    def refresh_trend_data(self, topics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Called by Celery beat schedule to refresh AcadEval_TrendBase PostgreSQL cache.
        """
        topic_list = topics or DEFAULT_TOPICS
        log.info("TrendScorerService: refreshing %d topics into PostgreSQL trendbase", len(topic_list))
        db = SessionLocal()
        summary = {}
        try:
            for t in topic_list:
                res = self.get_topic_trend(t, db=db)
                summary[t] = res.get("trend_status", "ok")
        finally:
            db.close()
        return summary

    @staticmethod
    def _compute_trend_from_records(topic: str, records: List[TrendBaseRecord], source: str) -> Dict[str, Any]:
        rec_map = {r.year: r.paper_count for r in records}
        current_year = datetime.now(timezone.utc).year
        last_year = current_year - 1
        three_years_ago = current_year - 3

        p_last = rec_map.get(last_year, 0)
        p_3yr = rec_map.get(three_years_ago, 0)
        trend_score = round((p_last - p_3yr) / float(max(p_3yr, 1)), 3)

        return {
            "topic": topic,
            "trend_score": trend_score,
            "growth_rate_pct": round(trend_score * 100.0, 1),
            "paper_count_3yr": sum(r.paper_count for r in records if r.year >= three_years_ago),
            "citation_velocity": round(sum(r.citation_count for r in records) / float(max(len(records), 1)), 1),
            "trend_status": "Emerging" if trend_score > 0.3 else ("Hot" if trend_score > 0.15 else "Steady"),
            "top_papers": [],
            "data_source": source,
            "papers_last_year": p_last,
            "papers_3_years_ago": p_3yr,
        }


# Singleton instance
trend_scorer_service = TrendScorerService()
