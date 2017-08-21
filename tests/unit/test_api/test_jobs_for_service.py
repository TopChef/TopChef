"""
Contains unit tests for :mod:`topchef.api.jobs_for_service`
"""
import json
import unittest.mock as mock
from tests.unit.test_api import TestAPI
from sqlalchemy.orm import Session
from flask import Request
from topchef.models import Service
from hypothesis import given, assume
from hypothesis.strategies import fixed_dictionaries, dictionaries, text
from tests.unit.model_generators.service import services
from topchef.serializers import JobDetail as JobDetailSerializer
from topchef.serializers import NewJob as NewJobSerializer
from topchef.api.jobs_for_service import JobsForServiceEndpoint
from topchef.models import ServiceList
from jsonschema import Draft4Validator as JSONSchemaValidator


class TestJobsForService(TestAPI):
    """
    Base class for unit testing the ``/services/<service_id>/jobs`` endpoint
    """
    def setUp(self) -> None:
        TestAPI.setUp(self)
        self.session = mock.MagicMock(spec=Session)
        self.request = mock.MagicMock(spec=Request)
        self.service_list = mock.MagicMock(spec=ServiceList)
        self.testing_app.add_url_rule(
            '/test_url/<service_id>', view_func=JobsForServiceEndpoint.as_view(
                JobsForServiceEndpoint.__name__
            )
        )


class TestGet(TestJobsForService):
    """
    Contains unit tests for the getter
    """
    @given(services())
    def test_get(self, service: Service) -> None:
        """

        :param service: The service for which the endpoint is to be tested
        :return:
        """
        endpoint = JobsForServiceEndpoint(
            self.session, self.request, self.service_list
        )
        response = endpoint.get(service)
        self.assertEqual(200, response.status_code)

        serializer = JobDetailSerializer()
        self.assertEqual(
            json.loads(response.data.decode('utf-8'))['data'],
            serializer.dump(service.jobs, many=True).data
        )


class TestPost(TestJobsForService):
    """
    Contains unit tests for the ``POST`` method of this endpoint, testing
    whether jobs can be made successfully
    """
    @given(dictionaries(text(), text()), services())
    def test_serialization_error(
            self, invalid_parameters: dict,
            service: Service
    ) -> None:
        """

        :param invalid_parameters: The incorrect parameters to test
        :param service: The service for which the job is to be made
        """
        serializer = NewJobSerializer()
        data, errors = serializer.load(invalid_parameters)
        assume(errors)

        self.request.get_json = mock.MagicMock(return_value=data)
        endpoint = JobsForServiceEndpoint(
            self.session, self.request, self.service_list
        )
        with self.assertRaises(endpoint.Abort):
            endpoint.post(service)

    @given(
        fixed_dictionaries({
            "parameters": dictionaries(text(), text())
        }),
        services()
    )
    def test_validation_error(
            self, parameters: dict, service: Service
    ) -> None:
        """

        :param parameters: The parameters that do not satisfy the JSON schema
        :param service: The service to test
        """
        validator = mock.MagicMock(spec=JSONSchemaValidator)
        validator_factory = mock.MagicMock(return_value=validator)
        validator.is_valid = mock.MagicMock(return_value=False)
        validator.iter_errors = mock.MagicMock(
            return_value={'error': 'message'}
        )

        self.request.get_json = mock.MagicMock(return_value=parameters)

        endpoint = JobsForServiceEndpoint(
            self.session, self.request, self.service_list, validator_factory
        )
        with self.assertRaises(endpoint.Abort):
            endpoint.post(service)

        self.assertTrue(endpoint.errors)

    @given(
        fixed_dictionaries({
            'parameters': dictionaries(text(), text())
        }),
        services()
    )
    def test_valid_post(
            self, parameters: dict, service: Service
    ) -> None:
        """
        Test that the job can be correctly created

        :param parameters: The new job parameters
        :param service: The service for which the job is to be created
        """
        validator = mock.MagicMock(spec=JSONSchemaValidator)
        validator_factory = mock.MagicMock(return_value=validator)
        validator.is_valid = mock.MagicMock(return_value=True)

        self.request.get_json = mock.MagicMock(return_value=parameters)

        endpoint = JobsForServiceEndpoint(
            self.session, self.request, self.service_list, validator_factory
        )
        response = endpoint.post(service)

        self.assertEqual(response.status_code, 201)
        self.assertIn('Location', response.headers)
