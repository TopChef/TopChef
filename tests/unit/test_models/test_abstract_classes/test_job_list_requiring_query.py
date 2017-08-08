"""
Contains unit tests for
:mod:`topchef.models.abstract_classes.job_list_requiring_query`
"""
import unittest
import unittest.mock as mock
from topchef.models.abstract_classes import JobListRequiringQuery
from topchef.models.interfaces.job import Job
from topchef.database.schemas import JobStatus
from sqlalchemy.orm import Session, Query
from hypothesis import given
from hypothesis.strategies import uuids, sampled_from, dictionaries, text
from hypothesis.strategies import integers
from uuid import UUID


class TestJobListRequiringQuery(unittest.TestCase):
    """
    Contains unit tests for the abstract job requiring a query
    """
    def setUp(self) -> None:
        """
        Set up mock p, AsyncIterator,arameters for the query, the session, and
        the mock job list.
        """
        self.session = mock.MagicMock(spec=Session)  # type: Session
        self.root_query = mock.MagicMock(spec=Query)  # type: Query

        self.job_list = self.MockJobListRequiringQuery(
            self.session, self.root_query
        )

    class MockJobListRequiringQuery(JobListRequiringQuery):
        """
        Stubs out the root job query with a mock root job query that will be
        given into this class at initialization
        """
        def __init__(self, db_session: Session, root_job_query: Query):
            super(self.__class__, self).__init__(db_session)
            self._root_query = root_job_query

        @property
        def root_job_query(self) -> Query:
            """

            :return: The mock query
            """
            return self._root_query


class TestInit(TestJobListRequiringQuery):
    """
    Contains unit tests for the abstract class's initializer
    """
    def test_init(self) -> None:
        """
        Tests that the initializer set the session correctly
        """
        self.assertEqual(self.job_list.session, self.session)


class TestGetItem(TestJobListRequiringQuery):
    """
    Contains unit tests for the ``__getitem__`` method of the job list
    """
    @given(uuids())
    def test_that_getitem_gets_a_job_by_query(self, job_id: UUID) -> None:
        """
        Tests that the getitem method correctly returns a job from the DB

        :param job_id: The ID of the job to get
        """
        job = self.job_list[job_id]
        self.assertEqual(
            mock.call(id=job_id), self.root_query.filter_by.call_args
        )
        expected_job_id = self.root_query.filter_by(id=job_id).first().id
        self.assertEqual(expected_job_id, job.id)


class TestSetItem(TestJobListRequiringQuery):
    """
    Contains unit tests for the ``__setitem__`` method of the job list
    """
    @given(
        uuids(), sampled_from(JobStatus),
        dictionaries(
            keys=text(), values=text()
        )
    )
    def test_that_setitem_sets_the_job_correctly(
            self, job_id: UUID, job_status: JobStatus,
            results: dict
    ):
        """

        :param job_id: The ID of the job to set
        :param job_status: The new job status
        :param results: The new job results
        """
        job = mock.MagicMock(spec=Job)
        job.status = job_status
        job.results = results
        self.job_list[job_id] = job
        database_job = self.session.add.call_args[0][0]
        self.assertEqual(database_job.status, job_status)
        self.assertEqual(database_job.results, results)


class TestDelItem(TestJobListRequiringQuery):
    """
    Contains unit tests for the ``__delitem__`` method of the job list. This
    method overloads ``del`` in order to allow easy deletion of jobs
    """
    @given(uuids())
    def test_that_delitem_deletes_the_job(self, job_id: UUID) -> None:
        """

        :param job_id: The ID of the job to delete
        """
        del self.job_list[job_id]
        self.assertEqual(
            mock.call(self.root_query.filter_by(id=job_id).first()),
            self.session.delete.call_args
        )


class TestContains(TestJobListRequiringQuery):
    """
    Contains unit tests for the ``__contains__`` method. This method overrides
    ``in`` in order to check for membership
    """
    @given(uuids())
    def test_that_contains_can_check_membership_for_job_ids(
            self, job_id: UUID
    ) -> None:
        """

        :param job_id: The UUID for which to check whether the list contains
            the job
        """
        self.assertIn(job_id, self.job_list)

        self.assertEqual(
            mock.call(id=job_id),
            self.root_query.filter_by.call_args
        )
        self.assertTrue(self.root_query.filter_by().count.called)

    def test_that_contains_can_check_membership_for_jobs(
            self
    ) -> None:
        """
        Tests that the ``in`` function can correctly check if a job is in
        the job list.
        """
        job = mock.MagicMock(spec=Job)
        self.assertIn(job, self.job_list)

        self.assertEqual(
            mock.call(id=job.id),
            self.root_query.filter_by.call_args
        )
        self.assertTrue(self.root_query.filter_by().count.called)


class TestIter(TestJobListRequiringQuery):
    """
    Contains unit tests for the ``iter`` method, which will return a
    generator of all the jobs available in the job list
    """
    def test_iter(self) -> None:
        """
        There should only be one job in the job iterable. This test checks
        that the method returns an iterable which correctly returns this job.
        """
        for job in self.job_list:
            self.assertIsInstance(
                job, Job
            )
            self.assertEqual(
                job.id, self.root_query.all()[0].id
            )


class TestAsyncIter(TestJobListRequiringQuery):
    """
    Contains unit tests for the ``__aiter__`` method, which should return an
    asynchronous generator
    """
    def test_async_iterator(self) -> None:
        """
        Tests that the asynchronous iterator works correctly
        """
        async_job_iterable = self.job_list.__aiter__()
        self.assertTrue(hasattr(async_job_iterable, '__anext__'))

        job = async_job_iterable.__anext__()
        self.assertIsNotNone(job)


class TestLen(TestJobListRequiringQuery):
    """
    Contains unit tests for the ``__len__`` method, which should return the
    number of jobs in the query set
    """
    @given(integers(max_value=pow(2, 63) - 1))
    def test_len(self, length: int) -> None:
        """
        Tests that the length of the job set is whatever the number of
        entries in the SQL query backing this job says it is.

        .. note::

            For some reason, ``unittest.mock`` won't let me set an integer
            bigger than the ``max_value`` specified in this test as a return
            value. Because of that, the max value on the integers needs to
            be constrained.

        :param length: A randomly-generated length
        """
        self.root_query.count = mock.MagicMock(return_value=length)
        self.assertEqual(length, len(self.job_list))
