from ..database.models import Service as DatabaseService
from ..database.models import Job as DatabaseJob
from uuid import UUID
from ..json_type import JSON_TYPE as JSON
from .job import Job
from .abstract_service import AbstractService
from .abstract_job import AbstractJob
from sqlalchemy.orm import Session
from typing import Optional, Iterator, Type, Union
import json


class Service(AbstractService):
    def __init__(self, database_service: DatabaseService):
        self.db_model = database_service

    @property
    def id(self) -> UUID:
        return self.db_model.id

    @property
    def name(self) -> str:
        return self.db_model.name

    @name.setter
    def name(self, new_name: str) -> None:
        self.db_model.name = new_name

    @property
    def description(self) -> str:
        return self.db_model.description

    @description.setter
    def description(self, new_description: str) -> None:
        self.db_model.description = new_description

    @property
    def job_registration_schema(self) -> JSON:
        return self.db_model.job_registration_schema

    @property
    def job_result_schema(self) -> JSON:
        return self.db_model.job_result_schema

    @property
    def is_service_available(self) -> bool:
        return self.db_model.is_service_available

    @is_service_available.setter
    def is_service_available(self, service_available: bool) -> None:
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
            database_job_constructor: Type[DatabaseJob]=DatabaseJob
    ) -> Job:
        db_job = database_job_constructor.new(self.db_model, parameters)
        return Job(db_job)

    @property
    def jobs(self) -> 'Service.JobCollection':
        return self.JobCollection(self.db_model)

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

    class JobCollection(AbstractService.AbstractJobCollection):
        """
        Base class for a collection of jobs
        """
        def __init__(self, service_db_model: DatabaseService) -> None:
            self.db_model = service_db_model

        def __getitem__(self, job_id: UUID) -> AbstractJob:
            db_job = self._get_job_model_guaranteed(job_id)
            return Job(db_job)

        def __setitem__(self, job_id: UUID, job: AbstractJob) -> None:
            if job_id != job.id:
                raise ValueError('The Job must match the Job ID')
            db_job = self._get_job_model_guaranteed(job_id)

            db_job.parameters = job.parameters
            db_job.results = job.results
            db_job.status = job.status

            self._session.add(db_job)

        def __delitem__(self, job_id: UUID) -> None:
            db_job = self._get_job_model_guaranteed(job_id)
            self._session.delete(db_job)

        def __len__(self) -> int:
            return self._session.query(DatabaseJob).filter_by(
                service=self.db_model
            ).count()

        def __iter__(self) -> Iterator[Job]:
            """
            :return: An iterable over all the jobs
            """
            db_jobs = self._session.query(DatabaseJob).filter_by(
                service=self.db_model
            ).all()

            return (Job(job) for job in db_jobs)

        def __contains__(self, item: Union[UUID, AbstractJob]) -> bool:
            if isinstance(item, AbstractJob):
                is_in_collection = self._check_membership_for_job(item)
            else:
                is_in_collection = self._check_membership_for_id(item)

            return is_in_collection

        @property
        def _session(self) -> Session:
            return Session.object_session(self.db_model)

        @property
        def _service_id(self) -> UUID:
            return self.db_model.id

        def _get_job_model_by_id(self, job_id: UUID) -> Optional[DatabaseJob]:
            return self._session.query(
                DatabaseJob
            ).filter_by(
                id=job_id
            ).first()

        def _get_job_model_guaranteed(self, job_id: UUID) -> DatabaseJob:
            db_model = self._get_job_model_by_id(job_id)

            if db_model is None:
                raise KeyError("A Job with that ID does not exist")
            else:
                return db_model

        def _check_membership_for_job(self, job: AbstractJob) -> bool:
            return bool(
                self._session.query(DatabaseJob).filter_by(
                    id=job.id
                ).count()
            )

        def _check_membership_for_id(self, job_id: UUID) -> bool:
            return bool(
                self._session.query(DatabaseJob).filter_by(
                    id=job_id
                ).count()
            )
