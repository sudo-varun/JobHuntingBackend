"""Command definitions for job applications.

Commands represent intentions to change state.
They are sent to the message bus for handling.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

class Command:
    pass

@dataclass
class CreateJobApplication(Command):
    """Command to create a new job application."""
    
    company: str
    position: str
    url: Optional[str] = None
    status: str = "Applied"
    date_applied: Optional[datetime] = None
    notes: Optional[str] = None
    salary: Optional[float] = None
    salary_estimated: bool = False


@dataclass
class UpdateJobApplicationStatus(Command):
    """Command to update a job application's status."""
    
    job_id: int
    status: str


@dataclass
class DeleteJobApplication(Command):
    """Command to delete a job application."""
    
    job_id: int
