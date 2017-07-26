import unittest
import unittest.mock as mock
from hypothesis import given
from hypothesis.strategies import dictionaries, text, integers
from topchef.database.models import Job as DatabaseJob
from topchef.models import Job
from topchef.database.models import JobStatus


class TestJob(unittest.TestCase):
    """
    Base class for testing jobs
    """
    def setUp(self):
        self.database_job = mock.MagicMock(
            spec=DatabaseJob
        )  # type: DatabaseJob
        self.job = Job(self.database_job)


class TestId(TestJob):
    def test_id(self):
        self.assertEqual(self.job.id, self.database_job.id)


class TestStatus(TestJob):
    def test_status(self):
        for status in {JobStatus.REGISTERED, JobStatus.ERROR,
                       JobStatus.WORKING, JobStatus.COMPLETED}:
            self.job.status = status
            self.assertEqual(self.job.status, self.database_job.status)


class TestParameters(TestJob):
    def test_parameters(self):
        self.assertEqual(self.job.parameters, self.database_job.parameters)


class TestResults(TestJob):
    @given(dictionaries(text(), integers()))
    def test_results(self, results):
        self.job.results = results
        self.assertEqual(results, self.job.results)
        self.assertEqual(self.job.results, self.database_job.results)
