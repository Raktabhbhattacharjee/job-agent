from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.file_service import FileService
from app.services.parser_service import ParserService
from app.services.resume_service import ResumeService
from app.schemas.resume import ResumeResponse

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post(
    "/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process a PDF resume",
)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload your resume here (PDF only!).

    Checks that it's a valid PDF, saves the file to disk with a unique UUID,
    rips out the raw text with PyMuPDF, and inserts the record into postgres.
    """
    # make sure it's actually a pdf before doing anything
    is_pdf = (file.content_type == "application/pdf") or (
        file.filename and file.filename.lower().endswith(".pdf")
    )
    if not is_pdf:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF only! Please convert your resume to a .pdf file and try again.",
        )

    # grab the bytes and save it with a unique name
    content = await file.read()
    file_path = FileService.save(file.filename, content)

    # rip the plain text out of the pdf pages
    extracted_text = ParserService.extract_resume(file_path=file_path)

    # save everything into the database
    resume = ResumeService.create(
        db=db,
        filename=file.filename,
        file_path=file_path,
        extracted_text=extracted_text,
    )

    return resume
