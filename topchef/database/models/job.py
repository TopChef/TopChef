"""
Contains a model for a job. A job is matched to a particular service. The job's
parameters must be an instance of the service schema, and the result must be
an instance of the result schema
"""
from .declarative_base import BASE
from ..schemas import database, JobStatus
from .service import Service
from sqlalchemy.orm import relationship
from uuid import UUID
from typing import Optional


class Job(BASE):
    __table__ = database.jobs

    id = __table__.c.job_id

    status = __table__.c.status
    results_id = __table__.c.results_id
    parameters_id = __table__.c.parameters_id

    service = relationship(Service, backref="jobs")

    def __init__(
            self, job_id: UUID, status: JobStatus, parameters_id: UUID,
            service: Service, results_id: Optional[UUID]=None
    ) -> None:
        self.id = job_id
        self.status = status
        self.parameters_id = parameters_id
        self.results_id = results_id
        self.service = service
