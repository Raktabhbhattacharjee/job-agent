import sys
from pathlib import Path

# Add project root to sys.path so running from either project root or inside app/ works
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI
from app.routers.analysis import router as analysis_router
from app.routers.jobs import router as jobs_router
from app.routers.recommendations import router as recommendation_router
from app.routers.resume import router as resume_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Job Agent API",
    description="Backend for the AI job agent project",
    version="0.1.0",
)

# allow frontend requests from localhost / Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# hook up routers
app.include_router(resume_router)
app.include_router(analysis_router)
app.include_router(jobs_router)
app.include_router(recommendation_router)


@app.get("/")
def root():
    """Quick sanity check to make sure the API is actually running."""
    return {
        "message": "hello from job-agent API!"
    }


@app.get("/health")
def health_check():
    """Health check endpoint for status monitoring."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
