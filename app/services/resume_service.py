from sqlalchemy.orm import Session
from app.models import Resume


class ResumeService:
    @staticmethod
    def create(
        db: Session, filename: str, file_path: str, extracted_text: str
    ) -> Resume:
        """Saves a new resume row into postgres and returns it."""
        resume = Resume(
            filename=filename, file_path=file_path, extracted_text=extracted_text
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume
