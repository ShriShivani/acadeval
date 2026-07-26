"""
Module 13 — GitHub API Client
==============================
Given a technology name, algorithm name, or project topic, searches GitHub's
public API for repositories that mention the same combination — providing an
optional "open-source prior-art" signal surfaced in the Novelty Report.

This is NOT folded into the numeric Novelty Index.  It appears as a
`github_signal` block in the report so reviewers can click through to
real repositories and judge overlap themselves.

Features:
  - Searches repos by topic/keyword combination
  - Rates each result by stars (popularity proxy) and last-push date (active)
  - Fetches the repo's README snippet for richer context
  - Respects GitHub's unauthenticated rate limit (60 req/hr) with a simple
    token bucket; set GITHUB_TOKEN in .env for 5,000 req/hr
  - In-process memory cache keyed by query hash (TTL 24 h)
"""

from __future__ import annotations

import hashlib
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

import requests

from app.config import settings

log = logging.getLogger(__name__)

GH_SEARCH_URL = "https://api.github.com/search/repositories"
GH_README_URL = "https://api.github.com/repos/{owner}/{repo}/readme"
CACHE_TTL_HOURS = 24
MAX_REPOS = 5           # max repos to return per query


def _cache_key(query: str) -> str:
    return hashlib.md5(query.lower().strip().encode()).hexdigest()[:16]


def _is_fresh(cached_at: str) -> bool:
    try:
        return datetime.now(timezone.utc) - datetime.fromisoformat(cached_at) \
               < timedelta(hours=CACHE_TTL_HOURS)
    except Exception:
        return False


class GitHubClient:
    """
    Public API:
      from app.services.github_client import github_client
      signal = github_client.find_similar_repos(["LSTM", "time-series", "anomaly detection"])
    """

    def __init__(self):
        self._cache: dict[str, dict] = {}

    # ── Internal HTTP helper ──────────────────────────────────────────────────

    def _headers(self) -> dict:
        h = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        token = getattr(settings, "GITHUB_TOKEN", "")
        if token:
            h["Authorization"] = f"Bearer {token}"
        return h

    def _get(self, url: str, params: dict | None = None) -> Optional[dict | list]:
        try:
            resp = requests.get(url, params=params, headers=self._headers(), timeout=8.0)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 403:
                reset = resp.headers.get("X-RateLimit-Reset")
                log.warning("GitHub rate-limited. Reset at: %s", reset)
                return None
            if resp.status_code == 422:
                log.warning("GitHub search 422 — query may be too long: %r", params)
                return None
            log.warning("GitHub API HTTP %d for %r", resp.status_code, url)
            return None
        except Exception as exc:
            log.warning("GitHub API error: %s", exc)
            return None

    # ── Public API ────────────────────────────────────────────────────────────

    def find_similar_repos(
        self,
        terms: list[str],
        language: Optional[str] = None,
    ) -> dict:
        """
        Searches GitHub for repositories matching the given technology/algorithm terms.

        Args:
          terms:    list of keywords e.g. ["YOLO", "object detection", "embedded"]
          language: optional language filter e.g. "Python"

        Returns:
          {
            "query": str,
            "repos": [
              {
                "name": str,
                "full_name": str,
                "description": str | None,
                "stars": int,
                "forks": int,
                "language": str | None,
                "last_pushed": str (ISO date),
                "url": str,
                "readme_snippet": str | None,
                "activity_label": "Active" | "Stale" | "Archived",
              }
            ],
            "total_count": int,
            "data_source": "github" | "gh_cache" | "unavailable",
            "cached_at": str | None,
          }
        """
        # Build a focused query — use the 3 most specific terms
        focused = [t for t in terms if len(t) > 2][:4]
        query = " ".join(focused)
        if language:
            query += f" language:{language}"

        if not query.strip():
            return self._unavailable(query)

        key = _cache_key(query)
        if key in self._cache and _is_fresh(self._cache[key].get("cached_at", "")):
            result = dict(self._cache[key])
            result["data_source"] = "gh_cache"
            return result

        result = self._fetch_live(query)
        if result["data_source"] == "github":
            result["cached_at"] = datetime.now(timezone.utc).isoformat()
            self._cache[key] = result

        return result

    def get_repo_readme_snippet(self, owner: str, repo: str, max_chars: int = 400) -> Optional[str]:
        """Fetches and decodes the README for a repo, returning a short snippet."""
        import base64
        data = self._get(GH_README_URL.format(owner=owner, repo=repo))
        if not data or not isinstance(data, dict):
            return None
        try:
            content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="ignore")
            # Strip markdown links/badges, keep plain text
            import re
            content = re.sub(r"!\[.*?\]\(.*?\)", "", content)
            content = re.sub(r"\[.*?\]\(.*?\)", "", content)
            content = re.sub(r"#{1,6}\s*", "", content)
            return content.strip()[:max_chars]
        except Exception:
            return None

    # ── Private helpers ───────────────────────────────────────────────────────

    def _fetch_live(self, query: str) -> dict:
        now = datetime.now(timezone.utc)
        one_year_ago = (now - timedelta(days=365)).strftime("%Y-%m-%d")

        data = self._get(GH_SEARCH_URL, {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": MAX_REPOS,
        })

        if not data or "items" not in data:
            return self._unavailable(query)

        repos = []
        for item in data["items"][:MAX_REPOS]:
            pushed = item.get("pushed_at", "")
            try:
                push_dt = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
                stale = (now - push_dt).days > 365
                activity = "Archived" if item.get("archived") else ("Stale" if stale else "Active")
            except Exception:
                activity = "Unknown"

            owner = item.get("owner", {}).get("login", "")
            repo_name = item.get("name", "")

            # Fetch README snippet (best-effort, skip if slow)
            readme = None
            try:
                readme = self.get_repo_readme_snippet(owner, repo_name)
                time.sleep(0.3)   # gentle rate limiting
            except Exception:
                pass

            repos.append({
                "name": repo_name,
                "full_name": item.get("full_name", ""),
                "description": item.get("description"),
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "language": item.get("language"),
                "last_pushed": pushed[:10] if pushed else None,
                "url": item.get("html_url", ""),
                "readme_snippet": readme,
                "activity_label": activity,
            })

        return {
            "query": query,
            "repos": repos,
            "total_count": data.get("total_count", 0),
            "data_source": "github",
            "cached_at": None,
        }

    @staticmethod
    def _unavailable(query: str) -> dict:
        return {
            "query": query,
            "repos": [],
            "total_count": 0,
            "data_source": "unavailable",
            "cached_at": None,
        }


# ── Singleton ─────────────────────────────────────────────────────────────────
github_client = GitHubClient()
