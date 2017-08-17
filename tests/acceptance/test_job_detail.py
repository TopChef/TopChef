"""
Tests that the job status and job results can be effectively modified
"""
import json
from tests.acceptance import AcceptanceTestCaseWithJob
from topchef.serializers import JobDetail as JobDetailSerializer
from uuid import uuid4


class TestJobDetail(AcceptanceTestCaseWithJob):
    """
    Base class for testing the ``/jobs/<job_id>`` endpoint
    """
    @property
    def url(self) -> str:
        """

        :return: The URL to the ``/jobs/<job_id>`` endpoint
        """
        return '%s/jobs/%s' % (self.app_url, self.job.id)

    @property
    def headers(self) -> dict:
        """

        :return: The HTTP connection headers
        """
        return {'Content-Type': 'application/json'}


class TestGet(TestJobDetail):
    def setUp(self) -> None:
        """
        Create a bad URL to the job
        """
        TestJobDetail.setUp(self)
        self.bad_job_id = uuid4()
        self.assertNotEqual(self.job.id, self.bad_job_id)

    @property
    def bad_url(self) -> str:
        return '%s/jobs/%s' % (self.app_url, self.bad_job_id)

    @property
    def expected_job_data(self) -> dict:
        """

        :return: The data expected to be returned for the job results
        """
        serializer = JobDetailSerializer()
        return serializer.dump(self.job).data

    def test_get_service_error(self) -> None:
        """
        Tests that a 404 error is returned if the Job with that particular
        ID does not exist
        """
        response = self.client.get(self.bad_url, headers=self.headers)
        self.assertEqual(404, response.status_code)

    def test_get_happy_path(self) -> None:
        """

        Tests that the correct data is returned when the service is serialized
        """
        response = self.client.get(self.url, headers=self.headers)
        self.assertEqual(200, response.status_code)
        response_body = json.loads(response.data.decode('utf-8'))
        self.assertEqual(self.expected_job_data, response_body['data'])
