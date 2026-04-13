import logging
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from job_hunting.logging_config import setup_logging
from job_hunting.domain import commands
from job_hunting import bootstrap, views
from job_hunting.adapters.scraper import JobScraper

setup_logging()
logger = logging.getLogger("job_hunting.api")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    logger.info("→ %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception("Unhandled error during %s %s", request.method, request.url.path)
        raise
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "← %s %s  status=%d  %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


bus = bootstrap.bootstrap()


class CreateJobRequest(BaseModel):
    company: str
    position: str
    url: Optional[str] = None
    status: Optional[str] = "Applied"
    date_applied: Optional[datetime] = None
    salary: Optional[float] = None
    salary_estimated: Optional[bool] = False


class UpdateStatusRequest(BaseModel):
    status: str


@app.get("/api/jobs/extract")
async def extract_job_details(url: Optional[str] = None):
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")

    try:
        scraper = JobScraper()
        details = scraper.extract_from_url(url)
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs", status_code=201)
async def create_job(req: CreateJobRequest):
    cmd = commands.CreateJobApplication(
        company=req.company,
        position=req.position,
        url=req.url,
        status=req.status,
        date_applied=req.date_applied,
        salary=req.salary,
        salary_estimated=req.salary_estimated,
    )
    bus.handle(cmd)
    return {"message": "OK"}


@app.put("/api/jobs/{job_id}")
async def update_job_status(job_id: int, req: UpdateStatusRequest):
    cmd = commands.UpdateJobApplicationStatus(
        job_id=job_id,
        status=req.status,
    )
    try:
        bus.handle(cmd)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": "OK"}


@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: int):
    cmd = commands.DeleteJobApplication(job_id=job_id)
    bus.handle(cmd)
    return {"message": "OK"}


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: int):
    result = views.view_job_by_id(job_id, bus.uow)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@app.get("/api/jobs")
async def get_jobs(status: Optional[str] = None, search: Optional[str] = None):
    params: dict[str, str] = {}
    if status is not None:
        params["status"] = status
    if search is not None:
        params["search"] = search

    jobs = views.list_jobs(params, bus.uow)
    return jobs
