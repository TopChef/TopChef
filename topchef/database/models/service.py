"""
Contains a model for a TopChef service. A service is any operation that maps a
 set of parameters to a set of results. An example of a service could be an
 ODMR resonance experiment, as it takes a set of experiment parameters and
 outputs the result.
"""
from ..schemas import database
from .declarative_base import BASE
from uuid import UUID


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
    job_registration_schema_reference = __table__.c.job_registration_schema_id
    job_result_schema_reference = __table__.c.job_result_schema_id
    is_service_available = __table__.c.is_service_available

    def __init__(
            self, service_id: UUID, name: str, description: str,
            registration_schema_id: UUID,
            result_schema_id: UUID
    ) -> None:
        self.id = service_id
        self.name = name
        self.description = description
        self.job_registration_schema_reference = registration_schema_id
        self.job_result_schema_reference = result_schema_id
        self.is_service_available = False
