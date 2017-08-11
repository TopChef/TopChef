"""
When working on the models, I found that getting the job list for a
particular service, and getting all the jobs on the API required very
similar code. The only difference between these two types is the "base" SQL
query on which they operate. In order to get all the jobs on the API,
I would have to run

.. sql::

    SELECT * FROM jobs

Whereas to get all the jobs for a particular service (let's say with ID =
1), I would have to run

.. sql::

    SELECT * FROM jobs
    INNER JOIN services ON jobs.service_id == service.service_id
    WHERE service_id = 1

The former query would map to SQLAlchemy as

.. python::

    session.query(Job).all()

and the latter would map to

.. python::

    session.query(Job).filter_by(service=Service).all()

Therefore, everything before

"""
import abc
from ..interfaces.job_list import JobList
from sqlalchemy.orm import Query, Session
from topchef.database.models import Job as DatabaseJob
from topchef.database.models.job import JobStatus as DatabaseJobStatus
from typing import Iterator, Sequence
from collections.abc import AsyncIterator
from topchef.models.interfaces.job import Job
from topchef.models.job import Job as JobModel
from copy import deepcopy
from uuid import UUID
from typing import Union


class JobListRequiringQuery(JobList, metaclass=abc.ABCMeta):
    _MODEL_TO_DB_JOB_STATUS = {
        Job.JobStatus.REGISTERED: DatabaseJobStatus.REGISTERED,
        Job.JobStatus.WORKING: DatabaseJobStatus.WORKING,
        Job.JobStatus.COMPLETED: DatabaseJobStatus.COMPLETED,
        Job.JobStatus.ERROR: DatabaseJobStatus.ERROR
    }

    @property
    @abc.abstractmethod
    def root_job_query(self) -> Query:
        """

        :return: The base SQLAlchemy query from which jobs are to be retrieved
        """
        raise NotImplementedError()

    @property
    def session(self) -> Session:
        return self._session

    def __init__(self, database_session: Session):
        self._session = database_session

    def __getitem__(self, job_id: UUID) -> Job:
        """

        :param job_id: The ID of the job to get
        :return: The job
        """
        return JobModel(self._safely_get_database_job(job_id))

    def __setitem__(self, job_id: UUID, job: Job) -> None:
        """

        :param job_id: The id of the job to get
        :param job: The parameters of the job to set
        """
        database_job = self._safely_get_database_job(job_id)
        database_job.status = self._MODEL_TO_DB_JOB_STATUS[job.status]
        database_job.results = job.results

        self.session.add(database_job)

    def __delitem__(self, job_id: UUID) -> None:
        """

        :param job_id: The ID of the job to delete
        """
        database_job = self._safely_get_database_job(job_id)
        self.session.delete(database_job)

    def __contains__(self, item: Union[UUID, Job]) -> bool:
        """
        Membership check for a job or job id in the job list

        :param item: The Job or Job ID to check
        :return: ``True`` if the job or job ID belongs in the job list,
            otherwise ``False
        """
        if isinstance(item, Job):
            is_in_collection = self._check_membership_for_job(item)
        else:
            is_in_collection = self._check_membership_for_id(item)

        return is_in_collection

    def __iter__(self) -> Iterator[Job]:
        """

        :return: An iterator that can iterate snychronously over all the
            jobs in the set
        """
        return (
            JobModel(db_job) for db_job in self._all_database_jobs
        )

    def __aiter__(self) -> AsyncIterator:
        """

        :return: The asynchronous job iterator that can asynchronously
            iterate over all the jobs.
        """
        return self._AsyncJobIterator(self._all_database_jobs)

    def __len__(self) -> int:
        return self.root_job_query.count()

    def _safely_get_database_job(self, job_id: UUID) -> DatabaseJob:
        job = self.root_job_query.filter_by(id=job_id).first()

        if job is None:
            raise KeyError('A job with id %s does not exist' % job_id)
        else:
            return job

    def _check_membership_for_job(self, job: Job) -> bool:
        return bool(
            self.root_job_query.filter_by(
                id=job.id
            ).count()
        )

    def _check_membership_for_id(self, job_id: UUID) -> bool:
        return bool(
            self.root_job_query.filter_by(
                id=job_id
            ).count()
        )

    @property
    def _all_database_jobs(self) -> Sequence[DatabaseJob]:
        return self.root_job_query.all()

    def __eq__(self, other: JobList) -> bool:
        """

        :param other: The other job list to compare
        :return: ``True`` if the jobs in this list are equal to jobs in the
            other list
        """
        return set(self) == set(other)

    class _AsyncJobIterator(AsyncIterator):
        def __init__(self, db_job_list: Sequence[DatabaseJob]) -> None:
            self.database_jobs = db_job_list
            self._last_iterated_index = 0

        def __aiter__(self) -> AsyncIterator:
            iterable = deepcopy(self)
            iterable._last_iterated_index = 0

            return iterable

        async def __anext__(self) -> Job:
            if self._last_iterated_index == len(self):
                raise StopAsyncIteration()
            else:
                db_job = self.database_jobs[self._last_iterated_index]
                self._last_iterated_index += 1
                return db_job

        def __len__(self):
            return len(self.database_jobs)

        class _JobAwaitable(object):
            def __init__(self, job: Job):
                self.job = job

            def __await__(self) -> Job:
                return self.job
