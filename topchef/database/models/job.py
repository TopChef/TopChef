"""
Contains a model for a job. A job is matched to a particular service. The job's
parameters must be an instance of the service schema, and the result must be
an instance of the result schema
"""
from .abstract_database_model import BASE
from ..schemas import database, JobStatus
from uuid import UUID, uuid4
from typing import Optional
from ...json_type import JSON_TYPE as JSON


class Job(BASE):

    __table__ = database.jobs

    id = __table__.c.job_id

    status = __table__.c.status  # type: JobStatus
    results = __table__.c.results  # type: JSON
    parameters = __table__.c.parameters  # type: JSON
    _service_id = __table__.c.service_id

    def __init__(
            self, job_id: UUID, status: JobStatus, parameters: JSON,
            service: 'Service', results: Optional[JSON]
    ) -> None:
        self.id = job_id
        self.status = status
        self.parameters = parameters
        self.results = results
        self.service = service

    @classmethod
    def new(cls, service: 'Service', parameters: JSON) -> 'Job':
        """

        :param Service service: The service for which this job is being
        created.
        :param JSON parameters: The job parameters
        :return: The newly-created job
        """
        new_id = uuid4()
        new_status = JobStatus.REGISTERED

        return cls(new_id, new_status, parameters, service, None)
