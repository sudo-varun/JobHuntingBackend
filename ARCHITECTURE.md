# Backend Architecture Guide

## Overview

The backend is structured using **Cosmic Python** (Domain-Driven Design + Ports & Adapters) principles. This guide explains the architecture and how to extend it.

## Layer Breakdown

### 1. Domain Layer (`domain/`)

**Purpose**: Core business logic, completely independent of frameworks or databases.

**Files**:

- `models.py`: The `JobApplication` aggregate root and `JobStatus` value object
- `repository.py`: Abstract `AbstractJobRepository` interface

**Key Principle**: No imports from Flask, SQLAlchemy, or any external dependencies here.

**Example**:

```python
from domain.model import JobApplication, JobStatus

# Pure domain logic - no database
job = JobApplication(company="Google", position="Engineer")
job.update_status("Interview")
assert job.status == JobStatus.INTERVIEW
```

### 2. Service Layer (`service_layer/`)

**Purpose**: Orchestrate domain logic and handle business rules.

**Files**:

- `services.py`: `JobApplicationService` coordinates between domain and repository

**Responsibilities**:

- Validate inputs
- Call domain methods
- Call repository methods
- Return domain objects

**Example**:

```python
service = JobApplicationService(repository)

# Service handles validation and coordination
job = service.create_job_application(
    company="Google",
    position="Engineer",
    status="Applied"
)
```

### 3. Adapter Layer (`adapters/`)

**Purpose**: Implement external system interactions (database, APIs, etc).

**Files**:

- `orm.py`: SQLAlchemy ORM models and domain ↔ ORM mapping
- `repository.py`: Concrete implementation of `AbstractJobRepository`

**Key Principle**: All database details are here. Domain never knows about SQLAlchemy.

**Flows**:

```
API Request
    ↓
Service (calls domain methods)
    ↓
Repository (queries database using ORM)
    ↓
ORM Model (SQLAlchemy object)
    ↓
Domain Model (via to_domain() conversion)
    ↓
Response
```

### 4. Entrypoints (`entrypoints/`)

**Purpose**: HTTP API handlers.

**Files**:

- `api.py`: Flask routes and request/response handling

**Key Principle**: No business logic here. Just parse requests, call services, return JSON.

**Example**:

```python
@jobs_bp.route("/api/jobs", methods=["POST"])
def create_job():
    data = request.get_json()
    # Validate syntax only
    if not data.get("company"):
        return {"error": "..."}, 400

    # Service handles business logic
    job = service.create_job_application(**data)
    return jsonify(job.to_dict()), 201
```

## Data Flow: Create Job Example

```
1. HTTP Request arrives at Flask route
   ↓
2. Entrypoint validates syntax (is it JSON? required fields?)
   ↓
3. Calls JobApplicationService.create_job_application()
   ↓
4. Service validates business logic (empty company name?)
   ↓
5. Creates JobApplication domain object (validates in __post_init__)
   ↓
6. Calls repository.add(job)
   ↓
7. Repository converts to ORM model (from_domain)
   ↓
8. SQLAlchemy saves to database
   ↓
9. ORM model converts back to domain (to_domain)
   ↓
10. Service returns domain object to entrypoint
    ↓
11. Entrypoint converts to dict and returns JSON
```

## Adding Features

### Example 1: Add a "Priority" Field

#### Step 1: Update Domain

```python
# domain/model.py
class JobApplication:
    priority: str = "Medium"  # Add field

    def set_priority(self, priority: str):
        if priority not in ["Low", "Medium", "High"]:
            raise ValueError("Invalid priority")
        self.priority = priority
        self.updated_at = datetime.utcnow()
```

#### Step 2: Update ORM

```python
# adapters/orm.py
class JobApplicationORM(Base):
    priority = Column(String(50), default="Medium")
```

#### Step 3: Update Service (if needed)

```python
# service_layer/services.py
def set_job_priority(self, job_id: int, priority: str):
    job = self.repository.get(job_id)
    job.set_priority(priority)  # Domain validation
    return self.repository.update(job)
```

#### Step 4: Add API Endpoint

```python
# entrypoints/api.py
@jobs_bp.route("/api/jobs/<int:job_id>/priority", methods=["PUT"])
def update_priority(job_id: int):
    data = request.get_json()
    job = service.set_job_priority(job_id, data["priority"])
    return jsonify(job.to_dict()), 200
```

**Why this works**: Domain has no database knowledge, so changes are clean and testable.

### Example 2: Add Email Notifications

#### Step 1: Create Adapter

```python
# adapters/email.py
class EmailService:
    def notify_status_change(self, job: JobApplication):
        # Send email using domain object
        pass
```

#### Step 2: Update Service

```python
# service_layer/services.py
def __init__(self, repository, email_service=None):
    self.repository = repository
    self.email_service = email_service

def update_job_application(self, job_id: int, **kwargs):
    job = self.repository.get(job_id)
    old_status = job.status

    # Update
    # ... existing code ...

    # Notify if status changed
    if old_status != job.status and self.email_service:
        self.email_service.notify_status_change(job)
```

**Why this works**: Service layer easily composes adapters, domain stays pure.

## Testing Strategy

Pure domain logic needs no database:

```python
# tests/test_domain.py
def test_job_application_creation():
    job = JobApplication(
        company="Google",
        position="Engineer"
    )
    assert job.status == JobStatus.APPLIED
    assert job.date_applied is not None

def test_invalid_job():
    with pytest.raises(ValueError):
        JobApplication(company="", position="Engineer")
```

Service tests can use mock repository:

```python
# tests/test_service.py
class MockRepository:
    def add(self, job):
        return job

def test_create_job():
    service = JobApplicationService(MockRepository())
    job = service.create_job_application("Google", "Engineer")
    assert job.company == "Google"
```

API tests use full stack:

```python
# tests/test_api.py
def test_create_job_api(client):
    response = client.post("/api/jobs", json={
        "company": "Google",
        "position": "Engineer"
    })
    assert response.status_code == 201
```

## Migration Path

### From Monolith to Services

When service grows large, extract parts:

```
# Today
service.create_job_application()
service.update_job_status()

# Tomorrow
JobApplicationService → microservice
```

### From Flask to FastAPI

Pure domain layer means zero changes needed:

```
# entrypoints/api.py changes, everything else stays same
```

### From SQLite to PostgreSQL

Update connection string, ORM changes only:

```python
# config.py
SQLALCHEMY_DATABASE_URI = "postgresql://..."
# Domain layer untouched!
```

## Dependencies

```
domain/          ← No external dependencies
    ↑
service_layer/   ← Depends on domain only
    ↑
adapters/        ← Depends on domain, SQLAlchemy
    ↑
entrypoints/     ← Depends on domain, service, Flask
    ↑
config/          ← Depends on nothing
```

**Golden Rule**: Dependencies point DOWN. Never UP. Domain never imports from any other layer.

## Troubleshooting

### "Import Error: Cannot import from domain"

Make sure you're importing from the `job_hunting` package:

```python
from job_hunting.domain import JobApplication  # ✓
from domain import JobApplication              # ✗
```

### "ORM and Domain models out of sync"

When adding fields:

1. Add to domain model
2. Add to ORM model
3. Update mapping in orm.py (to_domain/from_domain)

### "Service can't find repository"

Make sure it's passed to service on initialization:

```python
service = JobApplicationService(repository)  # ✓
service = JobApplicationService()            # ✗
```

## Next Steps

- Read [Cosmic Python](https://www.cosmicpython.com/)
- Look at test files to understand usage patterns
- Add your own aggregate roots following the same pattern
- Consider adding domain events for notifications
