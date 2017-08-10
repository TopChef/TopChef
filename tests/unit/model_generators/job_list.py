"""
Contains a generator for job lists
"""
from hypothesis.strategies import composite, lists
from tests.unit.model_generators.job import jobs
from topchef.models import JobList as JobListInterface
from topchef.models import Job as JobInterface
from typing import Iterable, MutableSequence, Iterator, Union
from uuid import UUID


class JobList(JobListInterface):
    """
    Implements the job list interface
    """
    def __init__(self, random_jobs: MutableSequence[JobInterface]):
        self._jobs = {job.id: job for job in random_jobs}

    @property
    def _job_ids(self) -> Iterable[UUID]:
        """

        :return: The job IDs generated here
        """
        return (job.id for job in self._jobs)

    def __getitem__(self, job_id: UUID) -> JobInterface:
        """

        :param job_id: The ID of the job to get
        :return: The Job
        """
        return self._jobs[job_id]

    def __setitem__(self, job_id: UUID, job: JobInterface) -> None:
        self._jobs[job_id] = job

    def __delitem__(self, job_id: UUID) -> None:
        del self._jobs[job_id]

    def __iter__(self) -> Iterator[JobInterface]:
        return iter(self._jobs.values())

    def __len__(self) -> int:
        return len(self._jobs.values())

    def __contains__(self, item: Union[UUID, JobInterface]) -> bool:
        return item in self._jobs.keys() or item in self._jobs.values()

    def __aiter__(self):
        raise Exception()

    def __eq__(self, other: JobListInterface) -> bool:
        return set(self) == set(other)


@composite
def job_lists(
        draw, jobs=lists(jobs())
) -> JobListInterface:
    return JobList(draw(jobs))
