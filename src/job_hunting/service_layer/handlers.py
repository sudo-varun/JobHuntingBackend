"""Command handlers for processing business logic.

Handlers contain the business logic for each command.
They use the UoW to interact with repositories.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from job_hunting.domain import commands
from job_hunting.domain.model import JobApplication, JobStatus

if TYPE_CHECKING:
    from . import unit_of_work

logger = logging.getLogger("job_hunting.handlers")


def handle_create_job_application(
    cmd: commands.CreateJobApplication, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    """Handle CreateJobApplication command."""
    logger.info("Creating job application: company=%s position=%s", cmd.company, cmd.position)
    with uow:
        date_applied = cmd.date_applied or datetime.now(timezone.utc)
        job = JobApplication(
            company=cmd.company,
            position=cmd.position,
            url=cmd.url,
            status=JobStatus.from_string(cmd.status),
            date_applied=date_applied,
            notes=cmd.notes,
            salary=cmd.salary,
            salary_estimated=cmd.salary_estimated,
        )
        uow.job_applications.add(job)
        uow.commit()
    logger.info("Job application created: company=%s position=%s", cmd.company, cmd.position)


def handle_update_job_status(
    cmd: commands.UpdateJobApplicationStatus, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    """Handle UpdateJobApplicationStatus command."""
    logger.info("Updating job status: job_id=%s status=%s", cmd.job_id, cmd.status)
    with uow:
        job = uow.job_applications.get(cmd.job_id)
        if not job:
            logger.warning("Job not found for status update: job_id=%s", cmd.job_id)
            raise ValueError(f"Job with id {cmd.job_id} not found")
        job.update_status(cmd.status)
        uow.job_applications.update(job)
        uow.commit()
    logger.info("Job status updated: job_id=%s status=%s", cmd.job_id, cmd.status)


def handle_delete_job_application(
    cmd: commands.DeleteJobApplication, uow: unit_of_work.AbstractUnitOfWork
) -> bool:
    """Handle DeleteJobApplication command."""
    logger.info("Deleting job application: job_id=%s", cmd.job_id)
    with uow:
        uow.job_applications.delete(cmd.job_id)
        uow.commit()
    logger.info("Job application deleted: job_id=%s", cmd.job_id)
    return True

EVENT_HANDLERS = {}

COMMAND_HANDLERS = {
    commands.CreateJobApplication: handle_create_job_application,
    commands.UpdateJobApplicationStatus: handle_update_job_status,
    commands.DeleteJobApplication: handle_delete_job_application,
}