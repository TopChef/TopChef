from tests.integration.test_database.test_models import \
    IntegrationTestCaseWithService
from topchef.database.models import Job
from topchef.database.schemas import JobStatus
from uuid import uuid4


class IntegrationTestCaseWithJob(IntegrationTestCaseWithService):
    """
    Base class for unit tests that have a job in them
    """
    @classmethod
    def setUpClass(cls):
        IntegrationTestCaseWithService.setUpClass()
        cls.job_id = uuid4()
        cls.job_status = JobStatus.WORKING
        cls.job = Job(cls.job_id, cls.job_status,
                      cls.valid_job_registration, cls.service,
                      cls.valid_result)

        cls.session.add(cls.job)
        cls.session.commit()

    @classmethod
    def tearDownClass(cls):
        cls.session.delete(cls.job)
        cls.session.commit()
        IntegrationTestCaseWithService.tearDownClass()

    def test_new(self):
        job = Job.new(self.service, self.valid_job_registration)
        self.assertNotEqual(self.job_id, job.id)
