"""
Contains unit tests for the ``JobListRequiringQuery`` abstract class
"""
import asyncio
from uuid import uuid4
from tests.integration.test_models import IntegrationTestCaseWithModels
from topchef.models.abstract_classes import JobListRequiringQuery
from sqlalchemy.orm import Query
from topchef.database.models import Job as DatabaseJob
from topchef.database.schemas.job_status import JobStatus
from typing import AsyncIterator
from topchef.models.interfaces import Job


class TestJobListRequiringQuery(IntegrationTestCaseWithModels):
    """
    Base class for testing the job list requiring a query
    """
    def setUp(self) -> None:
        """
        Create the job list
        """
        self.job_list = self.ConcreteJobList(self.session)
        self.invalid_job_id = uuid4()

    class ConcreteJobList(JobListRequiringQuery):
        """
        An instance of the job list that will work for all the jobs placed
        into the models
        """
        @property
        def root_job_query(self) -> Query:
            """

            :return: The query to get all database jobs
            """
            return self.session.query(DatabaseJob)


class TestGetItem(TestJobListRequiringQuery):
    """
    Contains integration tests for the ``__getitem__`` method
    """
    def test_getitem(self) -> None:
        """
        Tests that getting a job from the DB gets the correct job
        """
        job_from_db = self.job_list[self.job.id]
        self.assertEqual(self.job, job_from_db)

    def test_get_invalid_item(self) -> None:
        """
        Tests that getting an invalid job id will raise ``KeyError``
        """
        with self.assertRaises(KeyError):
            _ = self.job_list[self.invalid_job_id]


class TestSetItem(TestJobListRequiringQuery):
    """
    Contains integration tests for the ``__setitem__`` method
    """
    def test_setitem(self) -> None:
        """

        Tests that a mutable property of the job can be successfully set
        """
        job_from_db = self.job_list[self.job.id]
        job_from_db.status = JobStatus.COMPLETED
        self.job_list[self.job.id] = job_from_db

        second_job_from_db = self.job_list[self.job.id]
        self.assertEqual(second_job_from_db.status, JobStatus.COMPLETED)


class TestDelItem(TestJobListRequiringQuery):
    """
    Contains integration tests for the ``__delitem__`` method
    """
    def test_delitem(self) -> None:
        """
        Tests that the job can be deleted successfully
        """
        del self.job_list[self.job.id]

        with self.assertRaises(KeyError):
            _ = self.job_list[self.job.id]


class TestContains(TestJobListRequiringQuery):
    """
    Contains integration tests for the ``__contains__`` method
    """
    def test_contains_job_id(self) -> None:
        """
        Tests that the Job with the required job id exists in the DB
        """
        self.assertIn(self.job.id, self.job_list)

    def test_contains_job(self) -> None:
        """
        Tests that the job is in the job list
        """
        self.assertIn(self.job, self.job_list)

    def test_contains_invalid_id(self) -> None:
        """

        Tests that an invalid job is not in the job list
        """
        self.assertNotIn(self.invalid_job_id, self.job_list)


class TestIter(TestJobListRequiringQuery):
    """
    Contains unit tests for the ``__iter__`` method
    """
    def test_iter(self):
        """
        There should only be one job in the database. Get it, and make sure
        it is the same job just entered
        """
        job = iter(self.job_list).__next__()
        self.assertEqual(job, self.job)


class TestAsyncIter(TestJobListRequiringQuery):
    """
    Contains unit tests for the asynchronous iterator
    """
    @staticmethod
    async def get_async_job(iterator: AsyncIterator[Job]) -> Job:
        """

        :param iterator: The iterator from which jobs are retrieved
        :return: The job from the async iterator
        """
        return await iterator.__anext__()

    def test_async_job(self) -> None:
        """
        Tests that the async iterator correctly returns the job,
        when iterated over as a co-routine.
        """
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.get_async_job(self.job_list.__aiter__())
        )
        self.assertEqual(self.job, result)
