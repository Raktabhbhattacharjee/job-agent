from datetime import datetime
from sqlalchemy import DateTime, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    company: Mapped[str] = mapped_column(String(255), index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_type: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Full-time, Internship, Remote, etc.
    salary: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    skills: Mapped[list] = mapped_column(JSON, default=list)  # list of key skills mentioned in the job description
    url: Mapped[str] = mapped_column(String(1000), unique=True, index=True)  # job application link; unique prevents duplicate scrapes
    source: Mapped[str | None] = mapped_column(String(100), default="scraper")  # e.g. linkedin, indeed, remoteok
    dsa_level: Mapped[str | None] = mapped_column(String(50), default="Moderate", nullable=True)  # Low, Moderate, Heavy
    dsa_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    expectations: Mapped[list | None] = mapped_column(JSON, default=list, nullable=True)  # key things candidate will do or is expected to know
    company_intel: Mapped[str | None] = mapped_column(Text, nullable=True)  # brief summary of what the company builds
    posted_at: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
