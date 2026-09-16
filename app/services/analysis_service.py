from typing import Any
from sqlalchemy.orm import Session

from app.models.resume_analysis import ResumeAnalysis
from app.services.groq_service import GroqService


class AnalysisService:

    @staticmethod
    def save_analysis(
        db: Session,
        resume_id: int,
        data: dict[str, Any],
    ) -> ResumeAnalysis:
        """
        Saves the structured JSON returned from Groq into the resume_analysis table.
        If an analysis already exists for this resume_id, it updates it.
        """
        # check if an analysis already exists for this resume
        analysis = (
            db.query(ResumeAnalysis)
            .filter(ResumeAnalysis.resume_id == resume_id)
            .first()
        )

        if analysis:
            # update existing record
            analysis.name = data.get("name")
            analysis.email = data.get("email")
            analysis.phone = data.get("phone")
            analysis.summary = data.get("summary")
            analysis.skills = data.get("skills") or []
            analysis.experience = data.get("experience") or []
            analysis.education = data.get("education") or []
            analysis.projects = data.get("projects") or []
            analysis.preferred_roles = data.get("preferred_roles") or []
            analysis.raw_response = data
        else:
            # create new record
            analysis = ResumeAnalysis(
                resume_id=resume_id,
                name=data.get("name"),
                email=data.get("email"),
                phone=data.get("phone"),
                summary=data.get("summary"),
                skills=data.get("skills") or [],
                experience=data.get("experience") or [],
                education=data.get("education") or [],
                projects=data.get("projects") or [],
                preferred_roles=data.get("preferred_roles") or [],
                raw_response=data,
            )
            db.add(analysis)

        db.commit()
        db.refresh(analysis)
        return analysis

    @classmethod
    def analyze_and_save(
        cls,
        db: Session,
        resume_id: int,
        resume_text: str,
    ) -> ResumeAnalysis:
        """
        Full pipeline helper:
        1. Sends extracted resume text to Groq.
        2. Saves the generated JSON into postgres.
        """
        groq_result = GroqService.analyze_resume(resume_text=resume_text)
        return cls.save_analysis(db=db, resume_id=resume_id, data=groq_result)

    @staticmethod
    def get_by_resume_id(db: Session, resume_id: int) -> ResumeAnalysis | None:
        """Fetches the saved analysis for a given resume_id."""
        return (
            db.query(ResumeAnalysis)
            .filter(ResumeAnalysis.resume_id == resume_id)
            .first()
        )
