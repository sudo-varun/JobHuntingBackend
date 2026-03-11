"""Example tests showing the testing patterns."""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from job_hunting.domain.model import JobApplication, JobStatus
from job_hunting.service_layer.services import JobApplicationService


class MockJobRepository:
    """Mock repository for testing service layer."""

    def __init__(self):
        self.jobs = {}
        self.next_id = 1

    def add(self, job: JobApplication) -> JobApplication:
        job.id = self.next_id
        self.jobs[self.next_id] = job
        self.next_id += 1
        return job

    def get(self, job_id: int) -> JobApplication | None:
        return self.jobs.get(job_id)

    def get_all(self) -> list[JobApplication]:
        return list(self.jobs.values())

    def update(self, job: JobApplication) -> JobApplication:
        if job.id in self.jobs:
            self.jobs[job.id] = job
        return job

    def delete(self, job_id: int) -> None:
        self.jobs.pop(job_id, None)


class TestDomainModels:
    """Tests for pure domain logic."""

    def test_create_job_application(self):
        """Test creating a job application."""
        job = JobApplication(
            company="Google",
            position="Software Engineer"
        )
        assert job.company == "Google"
        assert job.position == "Software Engineer"
        assert job.status == JobStatus.APPLIED
        assert job.date_applied is not None

    def test_job_application_validation(self):
        """Test job application validation."""
        with pytest.raises(ValueError):
            JobApplication(company="", position="Engineer")

        with pytest.raises(ValueError):
            JobApplication(company="Google", position="")

    def test_update_status(self):
        """Test updating job status."""
        job = JobApplication(company="Google", position="Engineer")
        job.update_status("Interview")
        assert job.status == JobStatus.INTERVIEW

    def test_add_notes(self):
        """Test adding notes."""
        job = JobApplication(company="Google", position="Engineer")
        job.add_notes("Great opportunity")
        assert job.notes == "Great opportunity"

    def test_job_status_enum(self):
        """Test JobStatus enum."""
        assert JobStatus.APPLIED.value == "Applied"
        assert JobStatus.from_string("interview") == JobStatus.INTERVIEW


class TestJobApplicationService:
    """Tests for service layer."""

    @pytest.fixture
    def service(self):
        """Create service with mock repository."""
        repo = MockJobRepository()
        return JobApplicationService(repo)

    def test_create_job_application(self, service):
        """Test creating job via service."""
        job = service.create_job_application(
            company="Google",
            position="Engineer"
        )
        assert job.id is not None
        assert job.company == "Google"

    def test_get_job_application(self, service):
        """Test retrieving job via service."""
        created = service.create_job_application("Google", "Engineer")
        retrieved = service.get_job_application(created.id)
        assert retrieved.id == created.id

    def test_update_job_application(self, service):
        """Test updating job via service."""
        job = service.create_job_application("Google", "Engineer")
        updated = service.update_job_application(
            job.id,
            status="Interview",
            notes="Scheduled"
        )
        assert updated.status == JobStatus.INTERVIEW
        assert updated.notes == "Scheduled"

    def test_delete_job_application(self, service):
        """Test deleting job via service."""
        job = service.create_job_application("Google", "Engineer")
        success = service.delete_job_application(job.id)
        assert success
        assert service.get_job_application(job.id) is None

    def test_list_all_jobs(self, service):
        """Test listing all jobs."""
        service.create_job_application("Google", "Engineer")
        service.create_job_application("Amazon", "Manager")
        jobs = service.list_all_job_applications()
        assert len(jobs) == 2

    def test_job_statistics(self, service):
        """Test getting job statistics."""
        service.create_job_application("Google", "Engineer", status="Applied")
        service.create_job_application("Amazon", "Manager", status="Interview")

        stats = service.get_job_statistics()
        assert stats["total"] == 2
        assert stats["applied"] == 1
        assert stats["interview"] == 1
