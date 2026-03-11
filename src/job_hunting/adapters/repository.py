import abc
from typing import Set, Optional

from sqlalchemy.orm import Session

from job_hunting.domain import model


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[model.JobApplication]

    def add(self, job_application: model.JobApplication) -> None:
        self._add(job_application)
        self.seen.add(job_application)

    def get(self, job_id: int) -> model.JobApplication:
        job_application = self._get(job_id)
        if job_application:
            self.seen.add(job_application)
        return job_application

    def list_jobs(self, params: dict[str, str]) -> list[model.JobApplication]:
        job_applications = self._list(params)
        self.seen.update(job_applications)
        return job_applications

    def update(self, job_application: model.JobApplication):
        # For SQLAlchemy, the object is already tracked, so we just need to add it to seen
        self.seen.add(job_application)
        return job_application

    def delete(self, job_id: int) -> None:
        job_application = self._get(job_id)
        if job_application:
            self._delete(job_application)
            self.seen.discard(job_application)

    def get_all(self) -> list[model.JobApplication]:
        job_applications = self._list()
        self.seen.update(job_applications)
        job_applications = self._list({})
        self.seen.update(job_applications)
        return job_applications

    @abc.abstractmethod
    def _add(self, job_application: model.JobApplication):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, job_id: int) -> model.JobApplication:
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self, params: dict[str, str] = None) -> list[model.JobApplication]:
        raise NotImplementedError

    @abc.abstractmethod
    def _delete(self, job_application: model.JobApplication) -> None:
        raise NotImplementedError

class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session

    def _add(self, job_application):
        self.session.add(job_application)

    def _get(self, job_id: int) -> Optional[model.JobApplication]:
        try:
            return (
                self.session.query(model.JobApplication)
                .filter_by(id=job_id)
                .one_or_none()
            )
        except Exception:
            return None

    def _list(self, params: dict[str, str] = None) -> list[model.JobApplication]:
        query = self.session.query(model.JobApplication)
        
        if params:
            # Search by company or position (substring match)
            search = params.get("search", "").strip()
            if search:
                from sqlalchemy import or_
                query = query.filter(
                    or_(
                        model.JobApplication.company.ilike(f"%{search}%"),
                        model.JobApplication.position.ilike(f"%{search}%")
                    )
                )
            
            # Filter by status (exact match)
            status = params.get("status", "").strip()
            if status and status.lower() != "all":
                query = query.filter(model.JobApplication.status == status)
        
        try:
            return query.all()
        except Exception:
            return []

    def _delete(self, job_application: model.JobApplication) -> None:
        self.session.delete(job_application)
