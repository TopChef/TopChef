"""
Contains an implementation of the ``Service`` interface that pulls all the
required data from a SQLAlchemy model class.
"""
import json
from typing import Type, Callable
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from .interfaces import Service as ServiceInterface
from .interfaces import JobList as JobListInterface
from .abstract_classes import JobListFromQuery
from .job import Job
from ..database.models import Job as DatabaseJob
from ..database.models import Service as DatabaseService
from ..json_type import JSON_TYPE as JSON


class Service(ServiceInterface):
    """
    Provides a model class that gets all its data from an underlying
    database service already in the API's database
    """
    def __init__(
            self,
            database_service: DatabaseService,
            session_getter_for_model:
            Callable[[declarative_base()], Session]=Session.object_session
    ) -> None:
        self.db_model = database_service
        self._session_getter_for_model = session_getter_for_model

    @property
    def id(self) -> UUID:
        """

        :return: The service ID
        """
        return self.db_model.id

    @property
    def name(self) -> str:
        """

        :return: The service name
        """
        return self.db_model.name

    @name.setter
    def name(self, new_name: str) -> None:
        """

        :param new_name: The new name to be set in the API
        """
        self.db_model.name = new_name

    @property
    def description(self) -> str:
        """

        :return: A human-readable description for the service
        """
        return self.db_model.description

    @description.setter
    def description(self, new_description: str) -> None:
        """

        :param new_description: The desired new description
        """
        self.db_model.description = new_description

    @property
    def job_registration_schema(self) -> JSON:
        """

        :return: The JSON schema that must be satisfied in order to create a
            new job
        """
        return self.db_model.job_registration_schema

    @property
    def job_result_schema(self) -> JSON:
        """

        :return: The JSON schema that must be satisfied in order to post a
            result to the job
        """
        return self.db_model.job_result_schema

    @property
    def is_service_available(self) -> bool:
        """

        :return: A flag that indicates whether the service is ready to
            accept jobs
        """
        return self.db_model.is_service_available

    @is_service_available.setter
    def is_service_available(self, service_available: bool) -> None:
        """

        :param service_available: The desired value for the flag
        """
        self.db_model.is_service_available = service_available

    @classmethod
    def new(cls, name: str, description: str, registration_schema: JSON,
            result_schema: JSON, database_session: Session) -> 'Service':
        db_model = DatabaseService.new(
            name, description, registration_schema, result_schema
        )
        cls._write_database_model(db_model, database_session)
        return cls(db_model)

    def new_job(
            self,
            parameters: JSON,
            database_job_constructor: Type[DatabaseJob]=DatabaseJob.new
    ) -> Job:
        db_job = database_job_constructor(self.db_model, parameters)
        session = self._session_getter_for_model(self.db_model)
        session.add(db_job)

        return Job(db_job)

    @property
    def jobs(self) -> JobListInterface:
        return self._ListOfJobsForService(
            self, self._session_getter_for_model(self.db_model)
        )

    @staticmethod
    def _assert_json(json_to_set):
        try:
            json.loads(json_to_set)
        except json.JSONDecodeError as error:
            raise ValueError(
                'The input is not JSON', error
            )

    @staticmethod
    def _write_database_model(
            model: DatabaseService, session: Session
    ) -> None:
        session.add(model)

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.db_model.id))

    def __repr__(self) -> str:
        return '%s(database_service=%s, session_getter_for_model=%s)' % (
            self.__class__.__name__,
            self.db_model,
            self._session_getter_for_model
        )

    class _ListOfJobsForService(JobListFromQuery):
        def __init__(self, service: ServiceInterface, db_session: Session):
            super(self.__class__, self).__init__(db_session)
            self.service_id = service.id

        @property
        def root_job_query(self):
            return self.session.query(DatabaseJob).filter_by(
                service_id=self.service_id
            )
