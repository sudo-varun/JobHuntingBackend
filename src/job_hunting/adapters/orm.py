"""SQLAlchemy ORM configuration."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text, Table, MetaData, create_engine, Enum, Float, Boolean
from sqlalchemy.orm import registry

from job_hunting import config
from job_hunting.domain.model import JobApplication, JobStatus

metadata = MetaData()
mapper_registry = registry()
engine = create_engine(config.get_sqlite_uri())

job_applications = Table(
    "job_applications",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("company", String(255), nullable=False),
    Column("position", String(255), nullable=False),
    Column("url", String(255)),
    Column("status", Enum(JobStatus), nullable=False),
    Column("date_applied", DateTime, default=datetime.now(timezone.utc)),
    Column("notes", Text),
    Column("salary", Float),
    Column("salary_estimated", Boolean, default=False),
    Column("created_at", DateTime, default=datetime.now(timezone.utc)),
    Column("updated_at", DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)),
    Column("had_referral", Integer, default=0)
)
def start_mappers() -> None:
    """Configure SQLAlchemy mappers."""
    metadata.create_all(engine)
    mapper_registry.map_imperatively(JobApplication, job_applications)