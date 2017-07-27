"""
Contains integration tests for :mod:`topchef.models.service.Service`
"""
from uuid import uuid4
from tests.integration.test_models import IntegrationTestCaseWithModels


class TestService(IntegrationTestCaseWithModels):
    def setUp(self):
        IntegrationTestCaseWithModels.setUp(self)
        self.bad_job_id = uuid4()
        self.job_id = self.job.id


class TestGetJob(TestService):
    def setUp(self):
        TestService.setUp(self)
        self.assertNotEqual(self.job_id, self.bad_job_id)

    def test_getitem(self):
        self.assertEqual(
            self.service.jobs[self.job_id], self.job
        )

    def test_getitem_keyerror(self):
        with self.assertRaises(KeyError):
            _ = self.service.jobs[self.bad_job_id]


class TestSetJob(TestService):
    def setUp(self):
        TestService.setUp(self)
        self.job_result = {'result': 'data'}

    def test_setitem(self):
        self.job.results = self.job_result
        self.service.jobs[self.job.id] = self.job

        self.assertEqual(
            self.job_result,
            self.service.jobs[self.job_id].results
        )


class TestDeleteJob(TestService):
    def test_delitem(self):
        del self.service.jobs[self.job_id]

        with self.assertRaises(KeyError):
            _ = self.service.jobs[self.job_id]


class TestLength(TestService):
    def setUp(self):
        self.expected_job_length = 1  # type: int

    def test_length(self):
        self.assertEqual(self.expected_job_length, len(self.service.jobs))


class TestIterator(TestService):
    def test_iter(self):
        jobs = (job for job in self.service)
        self.assertIn(self.job, jobs)


class TestContains(TestService):
    def test_contains_job_id(self):
        self.assertIn(self.job_id, self.service.jobs)

    def test_contains_job(self):
        self.assertIn(self.job, self.service.jobs)

    def test_contains_bad_job_id(self):
        self.assertNotIn(self.bad_job_id, self.service.jobs)
