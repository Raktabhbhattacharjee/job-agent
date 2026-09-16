from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class ResumeAnalysisResponse(BaseModel):
    id: int
    resume_id: int
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    summary: str | None = None
    skills: list[str] = []
    experience: list[dict[str, Any]] = []
    education: list[dict[str, Any]] = []
    projects: list[dict[str, Any]] = []
    preferred_roles: list[str] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
