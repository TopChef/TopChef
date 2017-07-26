"""
Defines TopChef jobs
"""
import abc
from topchef.database.models import JobStatus


class AbstractJob(object, metaclass=abc.ABCMeta):
    """
    Interface for the job
    """
    @property
    @abc.abstractmethod
    def id(self):
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

    def __eq__(self, other: 'AbstractJob') -> bool:
        return self.id == other.id
