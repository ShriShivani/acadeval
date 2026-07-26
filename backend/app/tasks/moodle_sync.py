"""
Module 13 — Moodle Sync Celery Task
=====================================
Scheduled task that:
  1. Calls moodle_client.get_submissions() for the configured assignment
  2. Skips submissions already imported (tracked by moodle_submission_id)
  3. Downloads files to a temp directory under uploads/moodle/<submission_id>/
  4. Creates Project + ProjectFile rows in PostgreSQL
  5. Enqueues the Celery pipeline chain (Module 11) for each new project
  6. Records the imported submission ID to prevent duplicates on next run

Run manually:
  celery -A app.worker call scheduled.moodle_sync
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from celery.utils.log import get_task_logger

from app.worker import celery_app

log = get_task_logger(__name__)


@celery_app.task(name="scheduled.moodle_sync", bind=True, max_retries=2, default_retry_delay=60)
def moodle_sync(self):
    """
    Hourly Moodle sync task.  Safe to call multiple times (idempotent via
    the imported_moodle_ids tracking set).
    """
    try:
        from app.config import settings
        from app.services.moodle_client import moodle_client
        from app.tasks.pipeline import enqueue_pipeline
        from app.database import SessionLocal
        from app.models.project import Project, ProjectFile, PipelineStatus, SubmissionType
        from app.utils.files import get_file_type

        if not moodle_client.configured:
            log.info("moodle_sync: Moodle not configured — skipping.")
            return {"status": "skipped", "reason": "not_configured"}

        assignment_id = int(getattr(settings, "MOODLE_ASSIGNMENT_ID", 0))
        faculty_user_id = getattr(settings, "MOODLE_FACULTY_USER_ID", None)

        if not assignment_id:
            log.info("moodle_sync: MOODLE_ASSIGNMENT_ID not set — skipping.")
            return {"status": "skipped", "reason": "no_assignment_id"}

        db = SessionLocal()
        imported_count = 0
        skipped_count = 0

        try:
            submissions = moodle_client.get_submissions(assignment_id)
            log.info("moodle_sync: %d submissions found for assignment %d",
                     len(submissions), assignment_id)

            for sub in submissions:
                sub_id = sub.get("submission_id")

                # Check if already imported — look for project with this moodle ID in title/metadata
                # We store the moodle submission_id as a prefix in the title for traceability
                moodle_marker = f"[moodle:{sub_id}]"
                already_exists = db.query(Project).filter(
                    Project.title.like(f"%{moodle_marker}%")
                ).first()

                if already_exists:
                    skipped_count += 1
                    continue

                # Determine uploader — use configured faculty user or fall back to None
                uploader_id = None
                if faculty_user_id:
                    try:
                        uploader_id = uuid.UUID(str(faculty_user_id))
                    except Exception:
                        pass

                if not uploader_id:
                    log.warning("moodle_sync: MOODLE_FACULTY_USER_ID not set or invalid — skipping sub %s", sub_id)
                    continue

                # Download files
                dest_dir = Path(settings.UPLOAD_DIR) / "moodle" / str(sub_id)
                downloaded = moodle_client.download_files(sub, dest_dir)

                if not downloaded:
                    log.warning("moodle_sync: no files downloaded for submission %s", sub_id)
                    continue

                # Create Project row
                first_filename = downloaded[0].name
                project = Project(
                    student_id=uploader_id,
                    title=f"{moodle_marker} {first_filename}",
                    domain="Unclassified",          # Module 1 will classify this
                    submission_type=SubmissionType.document,
                    pipeline_status=PipelineStatus.uploaded,
                )
                db.add(project)
                db.flush()

                for local_path in downloaded:
                    db.add(ProjectFile(
                        project_id=project.id,
                        file_type=get_file_type(local_path.name),
                        original_filename=local_path.name,
                        storage_path=str(local_path),
                    ))

                db.commit()
                db.refresh(project)

                # Enqueue Celery pipeline
                job = enqueue_pipeline(str(project.id))
                if hasattr(project, "celery_task_id") and job:
                    project.celery_task_id = job.id
                    db.commit()

                imported_count += 1
                log.info("moodle_sync: imported sub %s → project %s", sub_id, project.id)

        finally:
            db.close()

        log.info("moodle_sync complete — imported=%d skipped=%d", imported_count, skipped_count)
        return {
            "status": "ok",
            "imported": imported_count,
            "skipped": skipped_count,
            "assignment_id": assignment_id,
        }

    except Exception as exc:
        log.exception("moodle_sync failed: %s", exc)
        raise self.retry(exc=exc)
