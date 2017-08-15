"""
Contains unit tests for the ``/services/<service_id>`` endpoint
"""
import json
import unittest
import unittest.mock as mock
from datetime import timedelta
from math import floor
from topchef.api.service_detail import ServiceDetail
from sqlalchemy.orm import Session
from flask import Flask, Request
from hypothesis import given
from topchef.models import Service, ServiceList
from topchef.serializers import ServiceDetail as ServiceSerializer
from hypothesis.strategies import booleans, text, timedeltas
from tests.unit.model_generators.service import services
from werkzeug.exceptions import BadRequest


class TestServiceDetail(unittest.TestCase):
    """
    Base class for unit testing the API
    """
    def setUp(self) -> None:
        """
        Set up some mock model classes and create an endpoint
        """
        self.session = mock.MagicMock(spec=Session)  # type: Session
        self.request = mock.MagicMock(spec=Request)  # type: Request
        self.service_list = mock.MagicMock(
            spec=ServiceList
        )  # type: ServiceList

        self._app = Flask(__name__)
        self._app.add_url_rule(
            '/', view_func=ServiceDetail.as_view(
                ServiceDetail.__name__, self.session
            )
        )

        self._context = self._app.test_request_context()

        self._context.push()

    def tearDown(self):
        """

        Pop the test request context
        """
        self._context.pop()


class TestGet(TestServiceDetail):
    """
    Contains unit tests for the ``get`` method
    """
    @given(services())
    def test_get(self, service: Service):
        endpoint = ServiceDetail(
            self.session, self.request, self.service_list
        )
        response = endpoint.get(service)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.data.decode('utf-8'))

        self._assert_data_equal(data['data'], service)

    def _assert_data_equal(self, data: dict, service: Service) -> None:
        serializer = ServiceSerializer()
        self.assertEqual(data, serializer.dump(service).data)


class TestPatch(TestServiceDetail):
    """
    Contains unit tests for the ``patch`` method
    """
    @given(services())
    def test_patch_no_body(self, service: Service) -> None:
        """
        Tests that the service timeout is reset if the endpoint is patched
        without a request body

        :param service: The service to patch
        """
        service.has_timed_out = False
        self.request.get_json = mock.MagicMock(side_effect=BadRequest())

        endpoint = ServiceDetail(
            self.session, self.request, self.service_list
        )
        response = endpoint.patch(service)
        self.assertEqual(200, response.status_code)
        self.assertFalse(service.has_timed_out)

    @given(services(), booleans())
    def test_patch_is_available(
            self, service: Service, is_available: bool
    ) -> None:
        """

        :param is_available: The new value for availability
        """
        body = {'is_available': is_available}
        self._send_patch_request(service, body)
        self.assertEqual(is_available, service.is_service_available)

    @given(services(), text())
    def test_patch_description(
            self, service: Service, description: str
    ) -> None:
        """

        :param service: The service to patch
        :param description: The new description
        """
        body = {'description': description}
        self._send_patch_request(service, body)
        self.assertEqual(description, service.description)

    @given(services(), text())
    def test_patch_name(
            self, service: Service, name: str
    ) -> None:
        """

        :param service: The service to patch
        :param name: The new name
        """
        body = {'name': name}
        self._send_patch_request(service, body)
        self.assertEqual(name, service.name)

    from hypothesis import settings

    @given(services(), timedeltas(min_delta=timedelta(microseconds=1)))
    @settings(perform_health_check=False)
    def test_patch_timeout_bigger_than_0(
            self, service: Service, timeout: timedelta
    ) -> None:
        body = {'timeout': timeout.total_seconds()}
        self._send_patch_request(service, body)
        self.assertEqual(
            floor(timeout.total_seconds()), service.timeout.total_seconds()
        )

    def _send_patch_request(
            self, service: Service, request_body: dict
    ) -> None:
        self.request.get_json = mock.MagicMock(return_value=request_body)
        endpoint = ServiceDetail(
            self.session, self.request, self.service_list
        )
        response = endpoint.patch(service)
        self.assertEqual(200, response.status_code)
