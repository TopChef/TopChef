"""
Contains a generator for making services
"""
from hypothesis.strategies import composite
from hypothesis.strategies import uuids, text, dictionaries, booleans
from tests.unit.model_generators.job import Job as MockJob
from tests.unit.model_generators.job_list import JobList as MockJobList
from tests.unit.model_generators.job_list import job_lists
from topchef.models import Service as ServiceInterface
from topchef.json_type import JSON_TYPE as JSON
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from typing import Callable
from topchef.database.models import Service as DatabaseService
from topchef.database.models import Job as DatabaseJob
from topchef.models import Job
from topchef.models import JobList as JobListInterface
from datetime import datetime


class Service(ServiceInterface):
    """
    A minimal implementation of the ``ServiceInterface`` that can be easily
    generated using hypothesis
    """
    def __init__(
            self,
            service_id: UUID,
            name: str,
            description: str,
            registration_schema: dict,
            result_schema: dict,
            is_service_available: bool,
            job_list: JobListInterface
    ) -> None:
        """

        :param service_id: The ID of the mock service
        :param name: The name of the mock service
        :param description: The service's description
        :param registration_schema: A random dictionary
        :param result_schema: A random dictionary
        :param is_service_available: A random boolean indicating whether the
            service is available
        :param job_list: The list of jobs belonging to this service
        """
        self._id = service_id
        self._name = name
        self._description = description
        self._registration_schema = registration_schema
        self._result_schema = result_schema
        self._is_service_available = is_service_available
        self._jobs = job_list

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, new_description: str) -> None:
        self._description = new_description

    @property
    def job_registration_schema(self) -> JSON:
        return self._registration_schema

    @property
    def job_result_schema(self) -> JSON:
        return self._result_schema

    @property
    def is_service_available(self) -> bool:
        return self._is_service_available

    @is_service_available.setter
    def is_service_available(self, service_available: bool) -> None:
        self._is_service_available = service_available

    @classmethod
    def new(
            cls,
            name: str,
            description: str,
            registration_schema: JSON,
            result_schema: JSON,
            database_session: Session
    ) -> ServiceInterface:
        service_id = uuid4()
        is_service_available = False
        return Service(
            service_id,
            name,
            description,
            registration_schema,
            result_schema,
            is_service_available,
            MockJobList(list())
        )

    def new_job(
            self, parameters: JSON,
            database_job_constructor: Callable[
                [DatabaseService, JSON], Job]=DatabaseJob.new
    ) -> Job:
        job_id = uuid4()
        new_job = MockJob(
            job_id, Job.JobStatus.REGISTERED, parameters, {},
            datetime.utcnow()
        )
        self._jobs += new_job

        return new_job

    @property
    def jobs(self) -> JobListInterface:
        return self._jobs

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self._id))

    def __repr__(self) -> str:
        constructor_args = {
            'service_id': self._id,
            'description': self._description,
            'name': self._name,
            'registration_schema': self._registration_schema,
            'result_schema': self._result_schema,
            'is_service_available': self._is_service_available,
            'job_list': self._jobs
        }

        argument_string = ', '.join(
            (
                '%s=%s' % (key, constructor_args[key])
            ) for key in constructor_args.keys()
        )

        return '%s(%s)' % (self.__class__.__name__, argument_string)

@composite
def services(
        draw,
        ids=uuids(),
        names=text(),
        descriptions=text(),
        registration_schemas=dictionaries(text(), text()),
        result_schemas=dictionaries(text(), text()),
        are_available=booleans(),
        service_job_lists=job_lists()
) -> ServiceInterface:
    return Service(
        draw(ids), draw(names), draw(descriptions),
        draw(registration_schemas), draw(result_schemas),
        draw(are_available), draw(service_job_lists)
    )
