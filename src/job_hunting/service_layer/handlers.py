"""Command handlers for processing business logic.

Handlers contain the business logic for each command.
They use the UoW to interact with repositories.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from job_hunting.domain import commands


from job_hunting.domain.model import JobApplication, JobStatus

if TYPE_CHECKING:
    from . import unit_of_work


def handle_create_job_application(
    cmd: commands.CreateJobApplication, uow: unit_of_work.AbstractUnitOfWork
) -> None:
    """Handle CreateJobApplication command."""
    with uow:
        # Parse date if provided
        date_applied = cmd.date_applied or datetime.now(timezone.utc)

        # Create domain object (validates)
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

        # Save via repository
        uow.job_applications.add(job)
        uow.commit()


def handle_update_job_status(
    cmd: commands.UpdateJobApplicationStatus, uow: unit_of_work.AbstractUnitOfWork
) -> JobApplication | None:
    """Handle UpdateJobApplicationStatus command."""
    with uow:
        job = uow.job_applications.get(cmd.job_id)
        if not job:
            return None

        # Update domain object (validates)
        job.update_status(cmd.status)

        # Save via repository
        updated_job = uow.job_applications.update(job)
        uow.commit()

        return updated_job


def handle_delete_job_application(
    cmd: commands.DeleteJobApplication, uow: unit_of_work.AbstractUnitOfWork
) -> bool:
    """Handle DeleteJobApplication command."""
    with uow:
        uow.job_applications.delete(cmd.job_id)
        uow.commit()

        return True

EVENT_HANDLERS = {}

COMMAND_HANDLERS = {
    commands.CreateJobApplication: handle_create_job_application,
    commands.UpdateJobApplicationStatus: handle_update_job_status,
    commands.DeleteJobApplication: handle_delete_job_application,
}