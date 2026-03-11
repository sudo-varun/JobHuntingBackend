# Job Hunting Backend - Domain-Driven Design with Flask

A clean, well-structured Python Flask API for managing job applications. Built using **Cosmic Python** architecture patterns for maintainability and scalability.

## Architecture Overview

This project follows the **Domain-Driven Design (DDD)** and **Ports & Adapters** patterns for a clean separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                   ENTRYPOINTS (API)                     │
│        (Flask routes in entrypoints/api.py)             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 SERVICE LAYER (Business Logic)          │
│         (JobApplicationService in service_layer/)       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│         DOMAIN (Core Business Logic - DB Agnostic)      │
│  - JobApplication (Aggregate Root)                      │
│  - JobStatus (Value Object)                             │
│  - AbstractJobRepository (Interface)                    │
└──────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│               ADAPTERS (External Systems)               │
│  - ORM Mapping (adapters/orm.py)                        │
│  - Repository Implementation (adapters/repository.py)   │
│  - Database Driver (SQLAlchemy)                         │
└─────────────────────────────────────────────────────────┘
```

### Directory Structure

```
backend/
├── pyproject.toml                    # Project metadata & dependencies (uv)
├── requirements.txt                  # Pinned dependencies
├── app.py                            # Entry point - wires everything
│
└── src/job_hunting/
    ├── __init__.py                   # Package init
    ├── config.py                     # Configuration
    │
    ├── domain/                       # Core business logic (DB-agnostic)
    │   ├── models.py                 # JobApplication, JobStatus
    │   ├── repository.py             # AbstractJobRepository interface
    │   └── __init__.py
    │
    ├── service_layer/                # Business logic orchestration
    │   ├── services.py               # JobApplicationService
    │   └── __init__.py
    │
    ├── adapters/                     # External system implementations
    │   ├── orm.py                    # ORM mapping
    │   ├── repository.py             # Repository implementation
    │   └── __init__.py
    │
    └── entrypoints/                  # HTTP API
        ├── api.py                    # Flask routes
        └── __init__.py
```

## Setup & Installation

### Using `uv` (Recommended)

1. Install uv:

```bash
# macOS
brew install uv

# Other platforms
pip install uv
```

2. Navigate and sync:

```bash
cd backend
uv sync
```

3. Run:

```bash
uv run python app.py
```

### Using Traditional pip

1. Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install:

```bash
pip install -r requirements.txt
```

3. Run:

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Get All Jobs

```
GET /api/jobs
```

### Get Specific Job

```
GET /api/jobs/<id>
```

### Create Job

```
POST /api/jobs
Content-Type: application/json

{
  "company": "Google",
  "position": "Software Engineer",
  "url": "https://...",
  "status": "Applied",
  "date_applied": "2026-02-18T10:30:00",
  "notes": "Good fit"
}
```

### Update Job

```
PUT /api/jobs/<id>
Content-Type: application/json

{
  "status": "Interview",
  "notes": "Scheduled"
}
```

### Delete Job

```
DELETE /api/jobs/<id>
```

### Health Check

```
GET /api/health
```

## Status Values

- `Applied` - Initial application
- `Interview` - In progress
- `Offer` - Offer received
- `Rejected` - Application rejected

## Key Design Principles

### 1. Separation of Concerns

- **Domain**: Pure business logic, no framework dependencies
- **Service**: Orchestrates domain and repositories
- **Adapters**: Handles database/external systems
- **Entrypoints**: HTTP handlers only, no business logic

### 2. Testability

Domain logic can be tested without a database:

```python
def test_job_creation():
    job = JobApplication(company="Google", position="Engineer")
    assert job.status == JobStatus.APPLIED
```

### 3. Flexibility

Easy to swap implementations:

- Change `SQLite` → `PostgreSQL` without touching domain
- Change `Flask` → `FastAPI` without touching domain
- Add `Celery` tasks without domain changes

## Future Enhancements

### Phase 2: Background Jobs

- Add Celery for async job processing
- Domain layer is pure - easy to test

### Phase 3: Domain Events

- Emit events when jobs change status
- Trigger notifications, webhooks, emails

### Phase 4: Additional Aggregates

- Interview schedule aggregate
- Resume aggregate with matching logic

## References

- [Cosmic Python](https://www.cosmicpython.com/) - DDD patterns
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)
- [Hexagonal Architecture](https://en.wikipedia.org/wiki/Hexagonal_architecture)
