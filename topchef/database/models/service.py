"""
Contains a model for a TopChef service. A service is any operation that maps a
 set of parameters to a set of results. An example of a service could be an
 ODMR resonance experiment, as it takes a set of experiment parameters and
 outputs the result.
"""
from ..schemas import database
from .abstract_database_model import BASE
from uuid import UUID, uuid4
from ...json_type import JSON_TYPE as JSON
from .job import Job
from sqlalchemy.orm import relationship


class Service(BASE):
    """
    The database model for a compute service. This service has one job
    parameters schema, and one job result schema. These must be satisfied in
    order to allow jobs to be submitted.
    """
    __table__ = database.services

    id = __table__.c.service_id
    name = __table__.c.name
    description = __table__.c.description
    job_registration_schema = __table__.c.job_registration_schema  # type: JSON
    job_result_schema = __table__.c.job_result_schema  # type: JSON
    is_service_available = __table__.c.is_service_available

    jobs = relationship(Job, backref='service', cascade='all, delete-orphan')

    def __init__(
            self, service_id: UUID, name: str, description: str,
            registration_schema: JSON,
            result_schema: JSON
    ) -> None:
        self.id = service_id
        self.name = name
        self.description = description
        self.job_registration_schema = registration_schema
        self.job_result_schema = result_schema
        self.is_service_available = False

    @classmethod
    def new(
            cls,
            name: str,
            description: str,
            registration_schema: JSON,
            result_schema: JSON
    ) -> 'Service':
        service_id = uuid4()

        return cls(
            service_id, name, description, registration_schema, result_schema
        )
