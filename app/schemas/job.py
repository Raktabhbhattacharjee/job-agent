from datetime import datetime
from pydantic import BaseModel, ConfigDict


class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str | None = None
    job_type: str | None = None
    salary: str | None = None
    description: str
    skills: list[str] | None = []
    url: str
    source: str | None = None
    dsa_level: str | None = "Moderate"
    dsa_reason: str | None = None
    expectations: list[str] | None = []
    company_intel: str | None = None
    posted_at: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScrapeResponse(BaseModel):
    source: str
    method: str = "api"
    tag_searched: str
    total_fetched: int
    total_saved: int
