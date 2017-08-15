"""
Contains acceptance tests for the ``/services`` endpoint. This is the first
endpoint to make use of the DB.
"""
import json

from tests.acceptance import AcceptanceTestCaseWithService
from tests.acceptance.test_cases.acceptance_test_case import AcceptanceTestCase


class ServicesEndpointTestCase(AcceptanceTestCaseWithService):
    """
    Provides properties common to testing the ``/services`` endpoint
    """
    @property
    def url(self) -> str:
        """

        :return: The URL to the ``/services`` endpoint
        """
        return '%s/services' % self.app_url

    @property
    def headers(self) -> dict:
        """

        :return: The headers to use for testing the API
        """
        return {'Content-Type': 'application/json'}


class TestGetEndpoint(ServicesEndpointTestCase):
    """
    Tests that the API is correctly able to retrieve a service from the DB
    """
    def test_get(self) -> None:
        response = self.client.get(self.url, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        response_body = json.loads(response.data.decode('utf-8'))
        self.assert_correct_data(response_body)

    def assert_correct_data(self, response_body: dict) -> None:
        """
        :param response_body: The body of the response
        """
        self.assertEqual(1, len(response_body['data']))
        service_data = response_body['data'][0]
        self.assertEqual(
            self.description, service_data['description']
        )
        self.assertEqual(
            self.service_name, service_data['name']
        )


class TestPostEndpoint(ServicesEndpointTestCase):
    """
    Tests that sending a ``POST`` request to the ``/services`` endpoint
    creates a new service
    """
    def setUp(self) -> None:
        """
        Create some test data for the service
        """
        AcceptanceTestCase.setUp(self)
        self.new_service_name = 'New Service'
        self.new_service_description = 'A Description for the New Service'
        self.job_registration_schema = {'type': 'object'}
        self.job_result_schema = {'type': 'object'}

    def test_post(self):
        response = self.client.post(
            self.url, headers=self.headers, data=json.dumps(self.data)
        )
        self.assertEqual(201, response.status_code)

    @property
    def data(self) -> dict:
        return {
            'name': self.new_service_name,
            'description': self.new_service_description,
            'job_registration_schema': self.job_registration_schema,
            'job_result_schema': self.job_result_schema
        }
