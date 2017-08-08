import unittest
import unittest.mock as mock
from hypothesis import given
from hypothesis.strategies import dictionaries, text, integers, sampled_from
from topchef.database.models import Job as DatabaseJob
from topchef.database.models import JobStatus as DatabaseJobStatus
from topchef.models.job import Job


class TestJob(unittest.TestCase):
    """
    Base class for testing jobs
    """
    def setUp(self) -> None:
        """
        Create a fake database model in order to test how the model class works
        """
        self.database_job = mock.MagicMock(
            spec=DatabaseJob
        )  # type: DatabaseJob
        self.job = Job(self.database_job)


class TestId(TestJob):
    """
    Contains unit tests for the ``id`` getter
    """
    def test_id(self) -> None:
        """

        Check that the Job ID is the same as that of the underlying database
        model
        """
        self.assertEqual(self.job.id, self.database_job.id)


class TestStatus(TestJob):
    """
    Contains unit tests for the job status enum
    """
    @given(sampled_from(Job.JobStatus))
    def test_status(self, desired_status: Job.JobStatus) -> None:
        """

        Tests that the job status enum works as intended. When the job
        status enum is set to a different value, the enum value for the
        underlying database model changes to the appropriate type as well.

        :param desired_status: A randomly-sampled job status to set
        """
        self.job.status = desired_status
        self.assertEqual(self.job.status, desired_status)
        self.assertEqual(
            self.MODEL_TO_DB_STATUS[desired_status],
            self.database_job.status
        )

    MODEL_TO_DB_STATUS = {
        Job.JobStatus.REGISTERED: DatabaseJobStatus.REGISTERED,
        Job.JobStatus.WORKING: DatabaseJobStatus.WORKING,
        Job.JobStatus.COMPLETED: DatabaseJobStatus.COMPLETED,
        Job.JobStatus.ERROR: DatabaseJobStatus.ERROR
    }


class TestParameters(TestJob):
    """
    Contains unit tests for the ``parameters`` property
    """
    def test_parameters(self) -> None:
        """
        Tests that the parameters match those of the underlying job
        """
        self.assertEqual(self.job.parameters, self.database_job.parameters)


class TestResults(TestJob):
    @given(dictionaries(text(), integers()))
    def test_results(self, results):
        self.job.results = results
        self.assertEqual(results, self.job.results)
        self.assertEqual(self.job.results, self.database_job.results)
