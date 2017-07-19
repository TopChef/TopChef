"""
Models job sets
"""
from .job import Job
from ..schemas import database
from ._declarative_base import BASE
from sqlalchemy.orm import relationship


class JobSet(BASE):
    __table__ = database.job_sets

    id = __table__.c.job_set_id
    description = __table__.c.description
    jobs = relationship(Job, backref='job_set')
