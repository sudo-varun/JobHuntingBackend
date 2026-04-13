"""Views for read-only queries (CQRS read side).

Views handle all GET requests directly without going through commands.
They read from the repository without modifying state.
"""
from __future__ import annotations

from job_hunting.domain.model import JobApplication
from job_hunting.service_layer.unit_of_work import AbstractUnitOfWork


def list_jobs(params: dict[str, str], uow: AbstractUnitOfWork) -> list[dict[str, str]]:
    """Get all job applications."""
    with uow:
        jobs = uow.job_applications.list_jobs(params)

        return [job.to_dict() for job in jobs]


def view_job_by_id(job_id: int, uow: AbstractUnitOfWork) -> dict[str, dict] | None:
    """Get a specific job application by ID."""
    with uow:
        job = uow.job_applications.get(job_id)
        return job.to_dict() if job else None

def view_job_statistics(uow: AbstractUnitOfWork) -> dict:
    """Get statistics about job applications."""
    with uow:
        jobs = uow.job_applications.get_all()
        stats = {
            "total": len(jobs),
            "applied": sum(1 for j in jobs if j.status.value == "Applied"),
            "interview": sum(1 for j in jobs if j.status.value == "Interview"),
            "offer": sum(1 for j in jobs if j.status.value == "Offer"),
            "rejected": sum(1 for j in jobs if j.status.value == "Rejected"),
        }
        return stats

