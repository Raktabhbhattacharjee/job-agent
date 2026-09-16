from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.resume import Resume
from app.schemas.resume_analysis import ResumeAnalysisResponse
from app.services.analysis_service import AnalysisService
from app.services.parser_service import ParserService

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post(
    "/{resume_id}",
    response_model=ResumeAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze a resume using Groq LLM",
)
def analyze_resume(resume_id: int, db: Session = Depends(get_db)):
    """
    Kicks off the Groq LLM to read through the resume text and extracts
    candidate skills, experience, projects, education, and target roles.
    """
    # 1. find the resume in the database
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with id {resume_id} not found",
        )

    # 2. if text wasn't extracted during upload, try parsing the pdf file now
    text_to_analyze = resume.extracted_text
    if not text_to_analyze and resume.file_path:
        try:
            text_to_analyze = ParserService.extract_resume(resume.file_path)
            resume.extracted_text = text_to_analyze
            db.commit()
            db.refresh(resume)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not extract text from the resume file: {str(e)}",
            )

    if not text_to_analyze:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume has no text content to analyze. Please upload a readable PDF.",
        )

    # 3. send to Groq and save results into postgres
    try:
        analysis = AnalysisService.analyze_and_save(
            db=db,
            resume_id=resume.id,
            resume_text=text_to_analyze,
        )
    except ValueError as e:
        # e.g. missing GROQ_API_KEY
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Groq API error during resume analysis: {str(e)}",
        )

    return analysis


@router.get(
    "/{resume_id}",
    response_model=ResumeAnalysisResponse,
    summary="Get saved analysis for a resume",
)
def get_analysis(resume_id: int, db: Session = Depends(get_db)):
    """
    Fetches already saved analysis for a resume without re-running Groq.
    """
    analysis = AnalysisService.get_by_resume_id(db=db, resume_id=resume_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No analysis found for resume {resume_id}. Run POST /analysis/{resume_id} first.",
        )
    return analysis