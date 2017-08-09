"""
Contains acceptance tests for the ``/services`` endpoint. This is the first
endpoint to make use of the DB.
"""
import json
from topchef import APP_FACTORY
from topchef.models.service_list import ServiceList
from topchef.serializers import JSONSchema
from tests.acceptance import AcceptanceTestCase
from sqlalchemy.orm import Session
from marshmallow import Schema, fields


class AcceptanceTestCaseWithService(AcceptanceTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Add a service to the DB
        """
        AcceptanceTestCase.setUpClass()
        cls.service_name = 'Testing Service'
        cls.description = 'Description for the Testing Service'

        cls.job_registration_schema = JSONSchema(
            title='Job Registration Schema',
            description='Must be fulfilled for an experiment'
        ).dump(cls.JobRegistrationSchema())

        cls.job_result_schema = JSONSchema(
            title='Job Result Schema',
            description='Must be fulfilled to post results'
        ).dump(cls.JobRegistrationSchema())

        session = Session(bind=APP_FACTORY.engine)

        service_list = ServiceList(session)
        cls.service = service_list.new(
            cls.service_name, cls.description, cls.job_registration_schema,
            cls.job_result_schema
        )
        session.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Delete the service from the DB
        """
        if hasattr(cls, 'service') and hasattr(cls, 'engine'):
            session = Session(bind=cls.engine)
            session.delete(cls.service)
            session.commit()
        AcceptanceTestCase.tearDownClass()

    class JobRegistrationSchema(Schema):
        value = fields.Int()


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


class TestPostEndpoint(AcceptanceTestCase):
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

    @property
    def data(self) -> dict:
        return {
            'name': self.new_service_name,
            'description': self.new_service_description,
            'job_registration_schema': self.job_registration_schema
        }