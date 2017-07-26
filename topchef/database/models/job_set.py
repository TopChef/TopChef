"""
Models job sets
"""
from .job import Job
from ..schemas import database
from .abstract_database_model import BASE
from sqlalchemy.orm import relationship
from uuid import UUID, uuid4
from typing import Iterable


class JobSet(BASE):
    __table__ = database.job_sets

    id = __table__.c.job_set_id
    description = __table__.c.description
    jobs = relationship(Job, backref='job_set')

    def __init__(
            self, job_set_id: UUID, description: str,
            jobs: Iterable[Job]
    ) -> None:
        self.id = job_set_id
        self.description = description
        self.jobs = jobs

    @classmethod
    def new(cls, description: str, jobs: Iterable[Job]) -> 'JobSet':
        job_set_id = uuid4()
        return cls(job_set_id, description, jobs)
