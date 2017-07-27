"""
Defines the interface for services. A TopChef service is an object that is
capable of processing jobs
"""
import abc
from uuid import UUID
from sqlalchemy.orm import Session
from topchef.json_type import JSON_TYPE as JSON
from topchef.models.abstract_job import AbstractJob
from topchef.database.models import BASE
from topchef.database.models import Job as DatabaseJob
from collections.abc import Iterable, MutableMapping
from typing import Iterator as IteratorType
from typing import Type, Union


class AbstractService(Iterable, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def id(self) -> UUID:
        """

        :return: The ID of the service
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    @name.setter
    @abc.abstractmethod
    def name(self, new_name: str) -> None:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """

        :return: A human-readable description of the service
        """
        raise NotImplementedError()

    @description.setter
    @abc.abstractmethod
    def description(self, new_description: str) -> None:
        """

        :param new_description: The new description
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def job_registration_schema(self) -> JSON:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def job_result_schema(self) -> JSON:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def is_service_available(self) -> bool:
        raise NotImplementedError()

    @is_service_available.setter
    @abc.abstractmethod
    def is_service_available(self, service_available: bool) -> None:
        raise NotImplementedError()

    @classmethod
    @abc.abstractclassmethod
    def new(
            cls,
            name: str,
            description: str,
            registration_schema: JSON,
            result_schema: JSON,
            database_session: Session) -> 'AbstractService':
        """
        Create a new service and save the details of this service to some
        persistent storage.

        :param name: The name of the newly-created service
        :param description: A human-readable description describing what the
            service does.
        :param registration_schema: A JSON schema describing the set of all
            JSON objects that are allowed as parameters for this server's jobs
        :param result_schema: A JSON schema describing the set of all JSON
            objects that are allowed as results for this server's jobs
        :param database_session: The SQLAlchemy session to which the
            database model is to be written
        :return: The newly-created service
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def new_job(
            self,
            parameters: JSON,
            database_job_constructor: Type[BASE]=DatabaseJob
    ) -> AbstractJob:
        """

        :param parameters:
        :param database_job_constructor: The type to be used to create a
            new job
        :return:
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def jobs(self) -> 'AbstractService.AbstractJobCollection':
        raise NotImplementedError()

    def __eq__(self, other: 'AbstractService') -> bool:
        return self.id == other.id

    def __iter__(self) -> IteratorType[AbstractJob]:
        return self.jobs.__iter__()

    class AbstractJobCollection(MutableMapping, metaclass=abc.ABCMeta):

        @abc.abstractmethod
        def __getitem__(self, job_id: UUID) -> AbstractJob:
            raise NotImplementedError()

        @abc.abstractmethod
        def __setitem__(self, job_id: UUID, job: AbstractJob) -> None:
            """
            Update the job with this ID, and write the update to some
            persistent storage

            :param job_id: The ID of the job to set
            :param job: The new job to set
            """
            raise NotImplementedError()

        @abc.abstractmethod
        def __delitem__(self, job_id: UUID) -> None:
            raise NotImplementedError()

        @abc.abstractmethod
        def __iter__(self) -> IteratorType[AbstractJob]:
            raise NotImplementedError()

        @abc.abstractmethod
        def __len__(self) -> int:
            raise NotImplementedError()

        @abc.abstractmethod
        def __contains__(self, item: Union[UUID, AbstractJob]) -> bool:
            """
            Membership test for the container. This method MUST be able to
            check whether a job or a job id is in the container

            :param item: The job or the Job ID for which membership is to be
                checked
            :return: ``True`` if the job belongs to this service
            """
            raise NotImplementedError()