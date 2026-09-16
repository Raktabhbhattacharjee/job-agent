from typing import Any
from sqlalchemy import and_, not_, or_
from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.resume_analysis import ResumeAnalysis


class RecommendationService:

    @staticmethod
    def _normalize_set(items: list[str] | None) -> set[str]:
        """Converts a list of strings into a lowercase cleaned set."""
        if not items:
            return set()
        cleaned = set()
        for item in items:
            if isinstance(item, str):
                cleaned.add(item.strip().lower())
        return cleaned

    @classmethod
    def calculate_match(
        cls,
        candidate_skills: list[str],
        preferred_roles: list[str],
        job: Job,
    ) -> dict[str, Any]:
        """
        Scores a single job against candidate skills and target roles (0 to 100).
        Computes matched skills, missing skills, and a clear explanation.
        """
        cand_skills_set = cls._normalize_set(candidate_skills)
        job_skills_set = cls._normalize_set(job.skills)

        # 1. Skill overlap calculation
        matched_set = cand_skills_set.intersection(job_skills_set)
        missing_set = job_skills_set.difference(cand_skills_set)

        # Base score from skill percentage
        if job_skills_set:
            skill_score = (len(matched_set) / len(job_skills_set)) * 60.0
        else:
            skill_score = 30.0 if matched_set else 15.0

        # Also search candidate skills inside job description text
        desc_lower = (job.description or "").lower()
        extra_matched_from_desc = set()
        for skill in cand_skills_set:
            if skill in desc_lower and skill not in matched_set:
                extra_matched_from_desc.add(skill)

        if extra_matched_from_desc:
            skill_score += min(len(extra_matched_from_desc) * 5.0, 15.0)

        # 2. Title & Role relevance bonus (up to 25 points)
        title_bonus = 0.0
        job_title_lower = (job.title or "").lower()
        for role in preferred_roles:
            role_lower = role.lower()
            # check words overlap
            role_words = [w for w in role_lower.split() if len(w) > 2]
            matching_words = [w for w in role_words if w in job_title_lower]
            if matching_words:
                title_bonus = max(title_bonus, 15.0 + (len(matching_words) * 5.0))

        # 3. Final total score capped between 0 and 100
        total_score = min(int(round(skill_score + title_bonus)), 100)

        # Format matched & missing lists preserving original or title-cased names
        matched_skills_list = [
            s.title() for s in matched_set.union(extra_matched_from_desc)
        ]
        missing_skills_list = [s.title() for s in list(missing_set)[:5]]

        # 4. Generate an informal, clear fit explanation
        reasons = []
        if matched_skills_list:
            reasons.append(
                f"Matches your skills in {', '.join(matched_skills_list[:3])}"
            )
        if title_bonus > 0:
            reasons.append(
                f"Strong title alignment with your target role ({job.title})"
            )
        if missing_skills_list:
            reasons.append(
                f"Bonus: learning {', '.join(missing_skills_list[:2])} would make you a top applicant"
            )

        fit_reason = (
            ". ".join(reasons) + "."
            if reasons
            else "General match based on profile domain."
        )

        return {
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "salary": job.salary,
            "url": job.url,
            "match_score": total_score,
            "matched_skills": matched_skills_list,
            "missing_skills": missing_skills_list,
            "fit_reason": fit_reason,
            "dsa_level": getattr(job, "dsa_level", "Moderate"),
            "company_intel": getattr(job, "company_intel", None),
        }

    @classmethod
    def get_recommendations_for_resume(
        cls,
        db: Session,
        resume_id: int,
        limit: int = 15,
        min_score: int = 20,
        role: str | None = None,
        experience_level: str | None = None,
    ) -> dict[str, Any]:
        """
        Scans all scraped jobs in PostgreSQL, ranks them against the candidate's
        resume analysis, and returns the top recommendations.
        """
        # 1. Grab candidate analysis
        analysis = (
            db.query(ResumeAnalysis)
            .filter(ResumeAnalysis.resume_id == resume_id)
            .first()
        )
        if not analysis:
            raise ValueError(
                f"No analysis found for resume id {resume_id}. Run POST /analysis/{resume_id} first!"
            )

        candidate_skills = analysis.skills or []
        preferred_roles = (
            [role.strip()]
            if role and role.strip()
            else (analysis.preferred_roles or [])
        )

        # 2. Fetch jobs from DB
        jobs_query = db.query(Job)
        normalized_level = (experience_level or "").strip().lower()
        if normalized_level == "internship":
            jobs_query = jobs_query.filter(
                or_(
                    Job.job_type.ilike("%intern%"),
                    Job.title.ilike("%intern%"),
                )
            )
        elif normalized_level == "experienced":
            jobs_query = jobs_query.filter(
                and_(
                    not_(Job.job_type.ilike("%intern%")),
                    not_(Job.title.ilike("%intern%")),
                    not_(Job.title.ilike("%entry level%")),
                )
            )

        jobs = jobs_query.all()

        # 3. Score every job
        scored_jobs = []
        for job in jobs:
            match_data = cls.calculate_match(
                candidate_skills=candidate_skills,
                preferred_roles=preferred_roles,
                job=job,
            )
            if match_data["match_score"] >= min_score:
                scored_jobs.append(match_data)

        # 4. Rank by match_score descending
        scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        top_recommendations = scored_jobs[:limit]

        return {
            "resume_id": resume_id,
            "candidate_name": analysis.name,
            "total_jobs_evaluated": len(jobs),
            "total_recommendations": len(top_recommendations),
            "recommendations": top_recommendations,
        }
