from uuid import uuid4
from topchef.models import Job, Service
from tests.integration.integration_test_case import IntegrationTestCase


class TestJob(IntegrationTestCase):
    """
    Base class for unit testing jobs
    """
    def setUp(self):
        IntegrationTestCase.setUp(self)
        self.service_id = uuid4()
        self.description = 'Testing service'
        self.job_id = uuid4()
        self.parameters = {'job': 'parameters'}
        self.job = Job(self.job_id, self.parameters)


class TestFromStorage(TestJob):
    """
    Base class for the ``from_storage`` constructor tests
    """
    def setUp(self):
        TestJob.setUp(self)

    def test_from_storage(self):
        session = self.session_factory()
        job = Job.from_storage(self.job_id, session, self.storage)

        self.assertEqual(self.job_id, job.id)


class TestWrite(TestJob):
    """
    Base class to test writing
    """
    def test_write(self):
        self.job.write(self.session_factory(), self.storage)
        job = Job.from_storage(
            self.job_id, self.session_factory(), self.storage
        )
        self.assertEqual(self.job_id, job.id)
        self.assertEqual(self.job_id, job.id)

