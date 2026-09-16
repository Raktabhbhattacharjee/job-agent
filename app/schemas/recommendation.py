from pydantic import BaseModel


class JobRecommendation(BaseModel):
    job_id: int
    title: str
    company: str
    location: str | None = None
    job_type: str | None = None
    salary: str | None = None
    url: str
    match_score: int
    matched_skills: list[str] | None = []
    missing_skills: list[str] | None = []
    fit_reason: str
    dsa_level: str | None = None
    company_intel: str | None = None


class RecommendationResponse(BaseModel):
    resume_id: int
    candidate_name: str | None = None
    total_jobs_evaluated: int
    total_recommendations: int
    recommendations: list[JobRecommendation]
