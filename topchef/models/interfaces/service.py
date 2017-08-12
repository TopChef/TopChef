"""
Defines the interface for services. A TopChef service is an object that is
capable of processing jobs. In practice, there exists a mapping between
services and experiment setups.
"""
import abc
from collections.abc import Iterable, AsyncIterable
from typing import Callable, AsyncIterator
from typing import Iterator as IteratorType
from uuid import UUID
from sqlalchemy.orm import Session
from topchef.models.interfaces.job_list import JobList
from topchef.database.models import Job as DatabaseJob
from topchef.database.models import Service as DatabaseService
from topchef.json_type import JSON_TYPE as JSON
from topchef.models.interfaces.job import Job


class Service(Iterable, AsyncIterable, metaclass=abc.ABCMeta):
    """
    The interface for the service, and the collection of jobs that the
    service manages. Describes the immutable and mutable properties of the
    service.

    .. note::

        After creating a schema, there is no way to change the job parameter
         or result schema. This is here to prevent rendering jobs that have
         already completed invalid, as they will no longer match the schema.

    """
    @property
    @abc.abstractmethod
    def id(self) -> UUID:
        """

        :return: The ID of the service. This is an object that can uniquely
            identify the service
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """

        :return: A human-readable name for the service
        """
        raise NotImplementedError()

    @name.setter
    @abc.abstractmethod
    def name(self, new_name: str) -> None:
        """
        Responsible for changing the name of the service

        :param str new_name: The new name of the service
        """
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
        """

        :return: A JSON schema representing the set of all valid JSON
            objects that can serve as parameters for this service's jobs
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def job_result_schema(self) -> JSON:
        """

        :return: A JSON schema representing the set of all valid JSON
            objects that can serve as results for this service's jobs
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def is_service_available(self) -> bool:
        """

        :return: A user-settable flag to indicate whether the service is
            available or not. Clients consuming a service SHOULD flip this flag
            to ``True`` when they are ready to accept services. Clients SHOULD
            flip this flag to ``False`` when they are shutting down. Clients
            posting jobs to this service MAY use this flag to check whether the
            service is available. Jobs posted to an unavailable service will
            still be pushed to the service's queue
        """
        raise NotImplementedError()

    @is_service_available.setter
    @abc.abstractmethod
    def is_service_available(self, service_available: bool) -> None:
        """

        :param service_available: The state to which the
            ``is_service_available`` flag is to be set
        """
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def new(
            cls,
            name: str,
            description: str,
            registration_schema: JSON,
            result_schema: JSON,
            database_session: Session) -> 'Service':
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
            database_job_constructor: Callable[
                [DatabaseService, JSON], Job]=DatabaseJob.new
    ) -> Job:
        """
        Using the

        :param parameters: The job parameters
        :param database_job_constructor: The type to be used to create a
            new job
        :return:
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def jobs(self) -> JobList:
        """

        :return: The list of all jobs that belong to this service
        """
        raise NotImplementedError()

    def __eq__(self, other: 'Service') -> bool:
        return self.id == other.id

    def __iter__(self) -> IteratorType[Job]:
        return self.jobs.__iter__()

    def __aiter__(self) -> AsyncIterator[Job]:
        return self.jobs.__aiter__()

    @abc.abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError()
