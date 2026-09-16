from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), unique=True)

    name: Mapped[str | None]
    email: Mapped[str | None]
    phone: Mapped[str | None]
    summary: Mapped[str | None]
    experience: Mapped[list] = mapped_column(JSON)
    education: Mapped[list] = mapped_column(JSON)
    skills: Mapped[list] = mapped_column(JSON)
    preferred_roles: Mapped[list] = mapped_column(JSON)
    projects: Mapped[list] = mapped_column(JSON)
    raw_response: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="analysis")
