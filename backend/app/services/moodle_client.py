"""
Module 13 — Moodle REST API Client & Celery Import Task
=========================================================
Pulls student assignment submissions from a college Moodle LMS instance via
its web-service REST API, downloads the attached files, and automatically
feeds them into the AcadEval+ pipeline (Module 11 Celery chain) — replacing
the manual "upload" step for institutions that use Moodle.

Configuration (add to .env):
  MOODLE_URL=https://moodle.yourcollege.edu
  MOODLE_TOKEN=your_webservice_token
  MOODLE_ASSIGNMENT_ID=123          # integer assignment ID in Moodle
  MOODLE_FACULTY_USER_ID=<uuid>     # AcadEval user ID to assign as uploader

Celery beat schedule (add to worker.py after this module is configured):
  "moodle-sync-hourly": {
      "task": "scheduled.moodle_sync",
      "schedule": crontab(minute=0),   # every hour
  }

REST API used:
  mod_assign_get_submissions   — list all submissions
  core_files_get_files         — resolve file URLs
  (direct download via token-authenticated GET)
"""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path
from typing import Optional

import requests

from app.config import settings

log = logging.getLogger(__name__)


class MoodleClient:
    """
    Thin wrapper around the Moodle web-service REST API.

    Public API:
      from app.services.moodle_client import moodle_client
      submissions = moodle_client.get_submissions(assignment_id=123)
      for sub in submissions:
          moodle_client.download_files(sub)
    """

    def __init__(self):
        self.base_url: str = getattr(settings, "MOODLE_URL", "").rstrip("/")
        self.token: str    = getattr(settings, "MOODLE_TOKEN", "")
        self.ws_url: str   = f"{self.base_url}/webservice/rest/server.php"

    @property
    def configured(self) -> bool:
        """Returns True only when MOODLE_URL and MOODLE_TOKEN are both set."""
        return bool(self.base_url and self.token)

    def _call(self, function: str, **extra_params) -> Optional[dict | list]:
        """Make a Moodle REST API call and return parsed JSON."""
        if not self.configured:
            log.warning("Moodle not configured — set MOODLE_URL and MOODLE_TOKEN in .env")
            return None
        params = {
            "wstoken":          self.token,
            "wsfunction":       function,
            "moodlewsrestformat": "json",
            **extra_params,
        }
        try:
            resp = requests.get(self.ws_url, params=params, timeout=15.0)
            resp.raise_for_status()
            data = resp.json()
            # Moodle signals errors inside a 200 response as {"exception": "..."}
            if isinstance(data, dict) and "exception" in data:
                log.error("Moodle API error: %s — %s", data.get("errorcode"), data.get("message"))
                return None
            return data
        except Exception as exc:
            log.error("Moodle API call failed (%s): %s", function, exc)
            return None

    # ── Submission listing ────────────────────────────────────────────────────

    def get_submissions(self, assignment_id: int) -> list[dict]:
        """
        Fetches all submissions for a given Moodle assignment.

        Returns a list of normalised submission dicts:
          {
            "submission_id": int,
            "user_id": int,           # Moodle user ID
            "status": str,            # "submitted" / "draft"
            "time_modified": int,     # Unix timestamp
            "files": [
              {
                "filename": str,
                "fileurl": str,       # authenticated download URL
                "filesize": int,
                "mimetype": str,
              }
            ]
          }
        """
        data = self._call("mod_assign_get_submissions", assignid=assignment_id)
        if not data:
            return []

        results = []
        for assignment_data in (data if isinstance(data, list) else [data]):
            for sub in assignment_data.get("submissions", []):
                if sub.get("status") != "submitted":
                    continue   # skip drafts

                files = []
                for plugin in sub.get("plugins", []):
                    if plugin.get("type") != "file":
                        continue
                    for filearea in plugin.get("fileareas", []):
                        for f in filearea.get("files", []):
                            # Append the wstoken to the download URL
                            url = f.get("fileurl", "")
                            if url and self.token not in url:
                                sep = "&" if "?" in url else "?"
                                url = f"{url}{sep}token={self.token}"
                            files.append({
                                "filename": f.get("filename", "file"),
                                "fileurl": url,
                                "filesize": f.get("filesize", 0),
                                "mimetype": f.get("mimetype", ""),
                            })

                if not files:
                    continue

                results.append({
                    "submission_id": sub.get("id"),
                    "user_id": sub.get("userid"),
                    "status": sub.get("status"),
                    "time_modified": sub.get("timemodified"),
                    "files": files,
                })

        log.info("Moodle: found %d submitted entries for assignment %d", len(results), assignment_id)
        return results

    def download_files(self, submission: dict, dest_dir: Path) -> list[Path]:
        """
        Downloads all files in a submission dict to dest_dir.
        Returns a list of local file paths that were successfully saved.
        """
        dest_dir.mkdir(parents=True, exist_ok=True)
        saved = []
        for f in submission.get("files", []):
            filename = f.get("filename", f"file_{uuid.uuid4().hex[:8]}")
            dest_path = dest_dir / filename
            url = f.get("fileurl", "")
            if not url:
                continue
            try:
                resp = requests.get(url, timeout=60, stream=True)
                resp.raise_for_status()
                with open(dest_path, "wb") as fh:
                    for chunk in resp.iter_content(chunk_size=8192):
                        fh.write(chunk)
                saved.append(dest_path)
                log.info("Moodle: downloaded %s (%d bytes)", filename, dest_path.stat().st_size)
            except Exception as exc:
                log.error("Moodle: failed to download %s — %s", filename, exc)
        return saved

    def get_user_info(self, moodle_user_id: int) -> Optional[dict]:
        """
        Fetches Moodle user profile to get email / full name for mapping to
        an AcadEval student account (used in moodle_sync to auto-create users).
        """
        data = self._call("core_user_get_users_by_field",
                          field="id", values=[0][0:0] + [moodle_user_id])
        # Moodle expects: values[0]=id
        data = self._call("core_user_get_users_by_field",
                          **{"field": "id", "values[0]": moodle_user_id})
        if data and isinstance(data, list) and data:
            u = data[0]
            return {
                "moodle_id": moodle_user_id,
                "fullname": u.get("fullname", ""),
                "email": u.get("email", ""),
                "username": u.get("username", ""),
            }
        return None


# ── Singleton ─────────────────────────────────────────────────────────────────
moodle_client = MoodleClient()
