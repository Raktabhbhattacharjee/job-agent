from typing import Any
from sqlalchemy.orm import Session

from app.models.job import Job


class JobService:

    @staticmethod
    def create_or_update_job(db: Session, job_data: dict[str, Any]) -> Job:
        """
        Saves a scraped job into postgres.
        If a job with the same URL already exists, it updates it to prevent duplicates.
        """
        url = job_data.get("url")
        existing_job = db.query(Job).filter(Job.url == url).first() if url else None

        if existing_job:
            for key, val in job_data.items():
                if hasattr(existing_job, key) and val is not None:
                    setattr(existing_job, key, val)
            db.commit()
            db.refresh(existing_job)
            return existing_job

        new_job = Job(
            title=job_data.get("title", ""),
            company=job_data.get("company", ""),
            location=job_data.get("location"),
            job_type=job_data.get("job_type"),
            salary=job_data.get("salary"),
            description=job_data.get("description", ""),
            skills=job_data.get("skills") or [],
            url=job_data.get("url", ""),
            source=job_data.get("source", "scraper"),
            dsa_level=job_data.get("dsa_level", "Moderate"),
            dsa_reason=job_data.get("dsa_reason"),
            expectations=job_data.get("expectations") or [],
            company_intel=job_data.get("company_intel"),
            posted_at=job_data.get("posted_at"),
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return new_job

    @classmethod
    def bulk_save_jobs(cls, db: Session, jobs_list: list[dict[str, Any]]) -> int:
        """
        Saves a batch of scraped jobs into the database with deduplication.
        Returns the number of jobs processed.
        """
        saved_count = 0
        for job_data in jobs_list:
            if not job_data.get("url") or not job_data.get("title"):
                continue
            cls.create_or_update_job(db=db, job_data=job_data)
            saved_count += 1
        return saved_count

    @staticmethod
    def list_jobs(db: Session, limit: int = 50, skip: int = 0) -> list[Job]:
        """Fetches latest jobs from the database."""
        return db.query(Job).order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
