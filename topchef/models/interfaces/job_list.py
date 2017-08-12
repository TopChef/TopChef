import abc
from collections.abc import MutableMapping, AsyncIterable
from uuid import UUID
from topchef.models.interfaces.job import Job
from typing import Iterator, AsyncIterator, Union


class JobList(MutableMapping, AsyncIterable, metaclass=abc.ABCMeta):
    """
    Describes an interface for manipulating a set of jobs posted to the API.
    The Job list should be iterating over all the jobs in the list.
    """
    @abc.abstractmethod
    def __getitem__(self, job_id: UUID) -> Job:
        """
        Given a job ID, this method must return a job with an ID
        corresponding to that job ID, or raise ``KeyError``.

        :param job_id: The ID of the job to retrieve, or the value of the
            job to retrieve
        :return: The job
        :raises: :exc:`KeyError` if a job with that ID does not exist
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def __setitem__(self, job_id: UUID, job: Job) -> None:
        """

        :param job_id: The ID of the job to set
        :param job: The new job that is to occupy that ID
        :raises: :exc:`KeyError` if a job with that ID does not exist
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def __delitem__(self, job_id: UUID) -> None:
        """

        :param job_id: The ID of the job to delete
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def __iter__(self) -> Iterator[Job]:
        """

        :return: An iterator that can iterate synchronously through all the
            jobs in the set
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def __len__(self) -> int:
        """

        :return: The number of jobs in the set
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def __contains__(self, job_id: Union[UUID, Job]) -> bool:
        """
        Membership test. This method MUST be able to check whether a Job or
        JobID is in the container

        :param job_id: The job or the Job ID for which membership is to be
            checked
        :return: ``True`` if the job belongs to this service
        """

    @abc.abstractmethod
    def __aiter__(self) -> AsyncIterator[Job]:
        """

        :return: An iterator that can asynchronously iterate over all the
            jobs in the set
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def __eq__(self, other: 'JobList') -> bool:
        """

        :param other: The other job list against which equality is to be
            determined
        :return: ``True`` if the equality definition is met, otherwise
            ``False``
        """
        raise NotImplementedError()
