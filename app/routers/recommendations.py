from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get(
    "/{resume_id}",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get tailored job recommendations for a resume",
)
def get_recommendations(
    resume_id: int,
    limit: int = Query(default=10, ge=1, le=50, description="Max jobs to recommend"),
    min_score: int = Query(
        default=15, ge=0, le=100, description="Minimum match percentage"
    ),
    role: str | None = Query(default=None, description="Optional role override"),
    experience_level: str | None = Query(
        default=None, description="internship or experienced"
    ),
    db: Session = Depends(get_db),
):
    """
    Compares candidate skills and preferred roles from the resume analysis
    against all scraped jobs in PostgreSQL, ranking the top matches.
    """
    try:
        results = RecommendationService.get_recommendations_for_resume(
            db=db,
            resume_id=resume_id,
            limit=limit,
            min_score=min_score,
            role=role,
            experience_level=experience_level,
        )
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}",
        )
