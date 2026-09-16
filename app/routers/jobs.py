from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import not_, or_
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.job import Job
from app.schemas.job import JobResponse, ScrapeResponse
from app.services.scraper_service import ScraperService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "/scrape",
    response_model=ScrapeResponse,
    status_code=status.HTTP_200_OK,
    summary="Scrape live jobs from LinkedIn India or RemoteOK",
)
def trigger_job_scrape(
    tag: str | None = Query(
        default=None,
        description="Keyword/tag to filter jobs by (e.g. 'python', 'react', 'full stack')",
    ),
    source: str = Query(
        default="linkedin_india",
        description="Scraping source: 'linkedin_india' (India internships) or 'remoteok' (Global remote)",
    ),
    location: str = Query(
        default="India",
        description="Location to search for (e.g. 'India', 'Bengaluru', 'Remote, India')",
    ),
    method: str = Query(
        default="api",
        description="Scraping method for RemoteOK: 'api' or 'playwright'",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=50,
        description="Maximum jobs to scrape in this request",
    ),
    db: Session = Depends(get_db),
):
    """
    Pulls live internships/jobs and enriches them with DSA requirement & company intel.
    Supports:
    - `source="linkedin_india"`: Real Indian internships from LinkedIn public guest search.
    - `source="remoteok"`: Global tech jobs from RemoteOK.
    """
    try:
        result = ScraperService.scrape_and_save(
            db=db,
            tag=tag,
            source=source,
            location=location,
            method=method,
            max_jobs=limit,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to scrape jobs: {str(e)}",
        )


@router.get(
    "/",
    response_model=list[JobResponse],
    summary="List scraped jobs from the database",
)
def list_jobs(
    query: str | None = Query(default=None, description="Search by title or company"),
    job_type: str | None = Query(
        default=None, description="Filter by job type (Full-time, Internship, etc.)"
    ),
    dsa_level: str | None = Query(
        default=None, description="Filter by DSA requirement level: Low, Moderate, Heavy"
    ),
    experience_level: str | None = Query(
        default=None, description="internship or experienced"
    ),
    unique_companies: bool = Query(
        default=True, description="Return only the newest job per company"
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Returns jobs saved in the database with search filtering, DSA level, and pagination.
    """
    q = db.query(Job)

    if query:
        search_pattern = f"%{query.strip()}%"
        q = q.filter(
            or_(
                Job.title.ilike(search_pattern),
                Job.company.ilike(search_pattern),
                Job.location.ilike(search_pattern),
            )
        )

    if job_type:
        q = q.filter(Job.job_type.ilike(f"%{job_type.strip()}%"))

    if dsa_level:
        q = q.filter(Job.dsa_level.ilike(f"%{dsa_level.strip()}%"))

    normalized_level = (experience_level or "").strip().lower()
    if normalized_level == "internship":
        q = q.filter(or_(Job.job_type.ilike("%intern%"), Job.title.ilike("%intern%")))
    elif normalized_level == "experienced":
        q = q.filter(
            not_(Job.job_type.ilike("%intern%")),
            not_(Job.title.ilike("%intern%")),
            not_(Job.title.ilike("%entry level%")),
        )

    jobs = q.order_by(Job.created_at.desc()).all()
    if unique_companies:
        seen_companies = set()
        unique_jobs = []
        for job in jobs:
            company_key = " ".join((job.company or "Unknown").lower().split())
            if company_key in seen_companies:
                continue
            seen_companies.add(company_key)
            unique_jobs.append(job)
        jobs = unique_jobs

    jobs = jobs[skip : skip + limit]
    return jobs


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get details of a specific job",
)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """
    Fetches a single job posting by ID.
    """
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found",
        )
    return job
