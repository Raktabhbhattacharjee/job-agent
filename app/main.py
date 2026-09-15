from fastapi import FastAPI
from app.routers.resume import router as resume_router

app = FastAPI(
    title="Job Agent API",
    description="Backend for the AI job agent project",
    version="0.1.0",
)

# hook up the resume upload router
app.include_router(resume_router)


@app.get("/")
def root():
    """Quick sanity check to make sure the API is actually running."""
    return {
        "message": "hello from job-agent API!"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
