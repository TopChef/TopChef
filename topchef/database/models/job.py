"""
Contains a model for a job. A job is matched to a particular service. The job's
parameters must be an instance of the service schema, and the result must be
an instance of the result schema
"""
from .declarative_base import BASE
from ..schemas import database
from .service import Service
from sqlalchemy.orm import relationship


class Job(BASE):
    __table__ = database.jobs

    id = __table__.c.job_id

    status = __table__.c.status
    results_id = __table__.c.results_id
    parameters_id = __table__.c.parameters_id

    service = relationship(Service, backref="jobs")
