"""Domain models for job applications."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import reconstructor

from job_hunting.domain.events import Event

class JobStatus(Enum):
    """Enumeration of possible job application statuses."""

    APPLIED = "Applied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"

    @classmethod
    def from_string(cls, value: str) -> "JobStatus":
        """Convert string to JobStatus enum."""
        try:
            return cls[value.upper()]
        except KeyError:
            return cls(value)

@dataclass
class JobApplication:
    """
    Job Application aggregate root.

    This is the main entity representing a job application.
    It encapsulates all business logic related to a job application.
    """

    company: str
    position: str
    events: list[Event] = field(default_factory=list)
    status: JobStatus = JobStatus.APPLIED
    url: Optional[str] = None
    date_applied: Optional[datetime] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    had_referral: bool = False
    notes: Optional[str] = None
    salary: Optional[int] = None
    salary_estimated: bool = False
    is_active: bool = True

    def __post_init__(self) -> None:
        """Validate and initialize the aggregate."""
        if not self.company or not self.company.strip():
            raise ValueError("Company name cannot be empty")
        if not self.position or not self.position.strip():
            raise ValueError("Position cannot be empty")

        if self.date_applied is None:
            self.date_applied = datetime.now(timezone.utc)

        if isinstance(self.status, str):
            self.status = JobStatus.from_string(self.status)

    @reconstructor
    def init_on_load(self):
        """SQLAlchemy reconstructor: called on ORM object load to initialize
        non-persistent attributes like `events` that aren't stored in the DB.
        Without this, instances loaded from the DB won't have `events` and
        code that expects it (like the unit of work event collector) will
        raise AttributeError.
        """
        # ensure events exists for objects loaded from the DB
        if not hasattr(self, "events") or self.events is None:
            self.events = []

    def update_status(self, new_status: JobStatus | str) -> None:
        """Update the job application status."""
        if isinstance(new_status, str):
            new_status = JobStatus.from_string(new_status)
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def add_notes(self, note: str) -> None:
        """Add or update notes for the job application."""
        self.notes = note
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "company": self.company,
            "position": self.position,
            "url": self.url,
            "status": self.status.value,
            "date_applied": self.date_applied.isoformat() if self.date_applied else None,
            "notes": self.notes,
            "salary": self.salary,
            "salary_estimated": self.salary_estimated,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __hash__(self):
        return hash((self.id, self.company))

class ExtractedJob(BaseModel):
    company: str
    position: str
    notes: str
    url: str
    salary: Optional[str] = None
    salary_estimated: bool = False

    def to_dict(self):
        return self.model_dump()