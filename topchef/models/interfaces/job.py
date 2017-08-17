"""
Defines TopChef jobs
"""
import abc
from enum import Enum
from uuid import UUID
from topchef.database.models import JobStatus
from datetime import datetime


class Job(object, metaclass=abc.ABCMeta):
    """
    Interface for the job
    """
    @property
    @abc.abstractmethod
    def id(self) -> UUID:
        """

        :return: The Job ID
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def status(self) -> JobStatus:
        """

        :return: The job status
        """
        raise NotImplementedError()

    @status.setter
    @abc.abstractmethod
    def status(self, new_status: JobStatus) -> None:
        """

        :param new_status: The new job status
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def parameters(self):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def results(self):
        raise NotImplementedError()

    @results.setter
    @abc.abstractmethod
    def results(self, new_results):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def date_submitted(self) -> datetime:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def parameter_schema(self) -> dict:
        """

        :return: The schema used to write down parameters
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def result_schema(self) -> dict:
        """

        :return: The schema used to write down valid results
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def __hash__(self) -> int:
        """

        :return: The hash of the number
        """
        raise NotImplementedError()

    def __eq__(self, other: 'Job') -> bool:
        return self.id == other.id

    class JobStatus(Enum):
        """
        The possible job statuses
        """
        REGISTERED = "REGISTERED"
        COMPLETED = "COMPLETED"
        WORKING = "WORKING"
        ERROR = "ERROR"
